# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from six import text_type as str

from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.resources.texts.local import Text as _Text
from capitains_nautilus.inventory.local import XMLFolderResolver
from capitains_nautilus.response import *
from capitains_nautilus.errors import InvalidURN, UnknownResource
from capitains_nautilus.cache import BaseCache
from capitains_nautilus import _cache_key


class Text(_Text):
    TIMEOUT = {
        "getValidReff":  604800
    }
    CACHE_CLASS = BaseCache  # By default cache has no cache

    def __init__(self, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        if isinstance(Text.CACHE_CLASS, BaseCache):
            self.cache = Text.CACHE_CLASS
        else:
            self.cache = Text.CACHE_CLASS()

    def getValidReff(self, level=1, reference=None):
        """ Cached method of the original object

        :param level:
        :param reference: Reference object
        :return: References
        """
        __cachekey__ = _cache_key("Text_GetValidReff", level, str(self.urn), str(reference))
        __cached__ = self.cache.get(__cachekey__)
        if __cached__:
            return __cached__
        else:
            __cached__ = super(Text, self).getValidReff(level, reference)
            self.cache.set(__cachekey__, __cached__, timeout=Text.TIMEOUT["getValidReff"])
            return __cached__


class NautilusRetriever(CTS):
    """ Nautilus Implementation of MyCapytain Endpoint

    :param folders: List of Capitains Guidelines structured folders
    :type folders: list(str)
    :param logger: Logging handler
    :type logger: logging
    :param auto_parse: Parses on first execution the resources given to build inventory
    :param resolver: Resolver to be used
    :ivar logger: Logging handler
    :type logger: logging
    :ivar resolver: Resolver for repository and text path
    :type resolver: XMLFolderResolver

    """
    def __init__(self,
                 folders=None, cache=None, pagination=True,
                 logger=None,
                 auto_parse=True, resolver=XMLFolderResolver):

        if not folders:
            folders = list()

        self.logger = logger
        if not logger:
            self.logger = logging.getLogger(__name__)
        self.__pagination = False
        self.resolver = resolver(resource=folders, cache=cache, logger=self.logger, auto_parse=auto_parse)
        self.resolver.TEXT_CLASS = Text

    def getCapabilities(self, inventory=None, output=XML, **kwargs):
        """ Retrieve the inventory information of an API

        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `capitains_nautilus.response`
        :type format: str
        :return: Formatted output of the inventory
        :rtype: str
        """
        return getcapabilities(
            *self.resolver.getCapabilities(
                inventory=inventory, pagination=self.__pagination, **kwargs
            ),
            output=output,
            **kwargs
        )

    def getPassage(self, urn, inventory=None, context=None, output=XML):
        """ Get a Passage from the repository

        :param urn: URN identifying the passage
        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `capitains_nautilus.response`
        :type format: str
        :param context: Unused parameter for now
        :return: Passage asked for, in given format
        """
        original_urn, urn, _text, metadata = self.getText(urn, inventory)

        if output == MY_CAPYTAIN:
            return _text.getPassage(urn.reference), metadata
        else:
            return getpassage(_text.getPassage(urn.reference), metadata, original_urn, output=output)

    def getPassagePlus(self, urn, inventory=None, context=None, output=XML):
        """Get a Passage and its metadata from the repository

        :param urn: URN identifying the passage
        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `capitains_nautilus.response`
        :type format: str
        :param context: Unused parameter for now
        :return: Passage asked for, in given format
        """
        passage, metadata = self.getPassage(
            urn, inventory, context,
            output=MY_CAPYTAIN
        )
        return getpassageplus(passage, metadata, urn, output=output)

    def getValidReff(self, urn, inventory=None, level=1, output=XML):
        """ Retrieve valid urn-references for a text

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param level: Depth of references expected
        :type level: int
        :return: Formatted response or list of references
        :rtype: str
        """
        original_urn, urn, _text, metadata = self.getText(urn, inventory)
        if urn.reference is not None and level <= len(urn.reference):
            if urn.reference.start and urn.reference.end:
                level = len(urn.reference)
            else:
                level = len(urn.reference) + 1

        if len(_text.citation) >= level:
            reffs = _text.getValidReff(level=level, reference=urn.reference)
            if urn.reference is not None:
                reffs = [
                    "{}:{}".format(urn.upTo(URN.VERSION), reff)
                    for reff in reffs
                ]
            else:
                reffs = ["{}:{}".format(urn.upTo(URN.VERSION), reff) for reff in reffs]
        else:
            return []
        return getvalidreff(reffs, level=level, request_urn=original_urn, output=output)

    def getPrevNextUrn(self, urn, inventory=None, output=XML):
        """ Retrieve valid previous and next URN

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :return: Formatted response with prev and next urn
        :rtype: str
        """
        passage, metadata = self.getPassage(
            urn, inventory,
            output=MY_CAPYTAIN
        )
        return getprevnext(passage, urn, output=output)

    def getFirstUrn(self, urn, inventory=None, output=XML):
        """ Retrieve valid first URN

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :return: Formatted response with first URN
        :rtype: str
        """
        passage, metadata = self.getPassage(
            urn, inventory,
            output=MY_CAPYTAIN
        )
        return getfirst(passage, urn, output=output)

    def getLabel(self, urn, inventory=None, output=XML):
        """ Retrieve label informations

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :return: Formatted response with metadata
        :rtype: str
        """
        passage, metadata = self.getPassage(
            urn, inventory,
            output=MY_CAPYTAIN
        )
        return getlabel(metadata, passage.urn, urn, output=output)

    def getText(self, urn, inventory=None):
        """ Retrieves a text in the inventory in case of partial URN or throw error when text is not accessible

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of
        :return: ( Original URN, Corrected URN,  Text, Metadata Text)
        """
        # If we don't have version
        original_urn = URN(urn)
        urn = original_urn
        if len(urn) == 4:
            matches, page, counter = self.resolver.getCapabilities(
                inventory=inventory, urn=urn.upTo(URN.WORK), category="edition"
            )
            if counter > 0:
                if urn.reference:
                    urn = URN("{0}:{1}".format(matches[0].urn, urn.reference))
                else:
                    urn = matches[0].urn
            else:
                raise UnknownResource()
        elif len(urn) < 4:
            raise InvalidURN()

        _text, metadata = self.resolver.getText(urn.upTo(URN.VERSION))

        return original_urn, urn, _text, metadata
