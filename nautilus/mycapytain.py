# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.resources.texts.local import Text as _Text, ContextPassage as _ContextPassage
from nautilus.inventory.local import XMLFolderResolver
from nautilus.response import *
from nautilus.errors import InvalidURN, UnknownResource
from werkzeug.contrib.cache import NullCache, BaseCache
from nautilus import _cache_key


class Text(_Text):
    TIMEOUT = {
        "getValidReff":  604800
    }
    CACHE_CLASS = NullCache  # By default cache has no cache

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
        __cache_key = _cache_key("Text_GetValidReff", level, str(reference))
        __cached = self.cache.get(__cache_key)
        if __cached:
            return __cached
        else:
            __cached = super(Text, self).getValidReff(level, reference)
            self.cache.set(__cache_key, __cached, timeout=Text.TIMEOUT["getValidReff"])
            return __cached


class NautilusEndpoint(CTS):
    """ Nautilus Implementation of MyCapytain Endpoint

    :param folders: List of Capitains Guidelines structured folders
    :type folders: list(str)

    :ivar resolver: Resolver for repository and text path
    :type resolver: XMLFolderResolver

    """
    def __init__(self, folders=[], cache=True):
        self.resolver = XMLFolderResolver(resource=folders)
        if cache is True:
            self.resolver.TEXT_CLASS = Text

    def getCapabilities(self, inventory=None, format=XML, **kwargs):
        """ Retrieve the inventory information of an API

        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `nautilus.response`
        :type format: str
        :return: Formatted output of the inventory
        :rtype: str
        """
        return getcapabilities(*self.resolver.getCapabilities(inventory=inventory, **kwargs), format=format, **kwargs)

    def getPassage(self, urn, inventory=None, context=None, format=XML):
        """ Get a Passage from the repository

        :param urn: URN identifying the passage
        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `nautilus.response`
        :type format: str
        :param context: Unused parameter for now
        :return: Passage asked for, in given format
        """
        original_urn, urn, _text, metadata = self.getText(urn, inventory)

        if format == MY_CAPYTAIN:
            return _text.getPassage(urn["reference"]), metadata
        else:
            return getpassage(_text.getPassage(urn["reference"]), metadata, original_urn, format=format)

    def getPassagePlus(self, urn, inventory=None, context=None, format=XML):
        """Get a Passage and its metadata from the repository

        :param urn: URN identifying the passage
        :param inventory: Name of the inventory
        :type inventory: text
        :param format: Format type of response. `nautilus.response`
        :type format: str
        :param context: Unused parameter for now
        :return: Passage asked for, in given format
        """
        passage, metadata = self.getPassage(
            urn, inventory, context,
            format=MY_CAPYTAIN
        )
        return getpassageplus(passage, metadata, urn, format=format)

    def getValidReff(self, urn, inventory=None, level=1, format=XML):
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

        if urn[6] is not None and level <= len(urn["reference"]):
            level = len(urn["reference"]) + 1

        if len(_text.citation) < level:
            reffs = []
        else:
            reffs = _text.getValidReff(level=level)
            if urn[6] is not None:
                reffs = [
                    "{}:{}".format(urn["text"], reff)
                    for reff in reffs
                    if reff.startswith("{}.".format(urn[6]))
                ]
            else:
                reffs = ["{}:{}".format(urn["text"], reff) for reff in reffs]

        return getvalidreff(reffs, level=level, request_urn=original_urn, format=format)

    def getPrevNextUrn(self, urn, inventory=None):
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
            format=MY_CAPYTAIN
        )
        return getprevnext(passage, urn, format=format)

    def getFirstUrn(self, urn, inventory=None):
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
            format=MY_CAPYTAIN
        )
        return getfirst(passage, urn, format=format)

    def getLabel(self, urn, inventory=None):
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
            format=MY_CAPYTAIN
        )
        return getlabel(metadata, passage.urn, urn, format=format)

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
                inventory=inventory, urn=urn["work"], category="edition"
            )
            if counter > 0:
                if urn["reference"]:
                    urn = URN("{0}:{1}".format(matches[0].urn, urn["reference"]))
                else:
                    urn = matches[0].urn
            else:
                raise UnknownResource()
        elif len(urn) < 4:
            raise InvalidURN()

        _text, metadata = self.resolver.getText(urn["text"])

        return original_urn, urn, _text, metadata
