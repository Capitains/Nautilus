# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
from six import text_type as str

from MyCapytain.resources.inventory import TextInventory, TextGroup, Work, Citation
from MyCapytain.resources.texts.local import Text
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import xmlparser
from capitains_nautilus.errors import *
from glob import glob
import os.path
from capitains_nautilus.inventory.proto import InventoryResolver
from capitains_nautilus import _cache_key
from capitains_nautilus.cache import BaseCache
import logging


class XMLFolderResolver(InventoryResolver):
    """ XML Folder Based resolver.

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]
    :param name: Key used to differentiate Repository and thus enabling different repo to be used
    :type name: str
    :param inventories:
    :type inventories:
    :param cache: Cache object to be used for the inventory
    :type cache: BaseCache
    :param logger: Logging object
    :type logger: logging

    :cvar TEXT_CLASS: Text Class [not instantiated] to be used to parse Texts. Can be changed to support Cache for example
    :type TEXT_CLASS: Text
    :ivar inventory_cache_key: Werkzeug Cache key to get or set cache for the TextInventory
    :ivar texts_cache_key:  Werkzeug Cache key to get or set cache for lists of metadata texts objects
    :ivar texts_parsed:  Werkzeug Cache key to get or set cache for lists of parsed texts objects
    :ivar texts: List of Text Metadata objects
    :ivar source: Original resource parameter

    .. warning :: This resolver does not support inventories
    """
    TEXT_CLASS = Text

    def __init__(self, resource, inventories=None, cache=None, name=None, logger=None, auto_parse=True):
        """ Initiate the XMLResolver

        """
        super(XMLFolderResolver, self).__init__(resource=resource)

        if not isinstance(cache, BaseCache):
            cache = BaseCache()

        self.__inventories__ = inventories
        self.__cache = cache
        self.name = name

        self.logger = logger
        if not logger:
            self.logger = logging.getLogger(name)

        if not name:
            self.name = "repository"
        self.TEXT_CLASS = XMLFolderResolver.TEXT_CLASS
        self.works = []

        self.inventory_cache_key = _cache_key("Nautilus", "Inventory", "Resources", self.name)
        self.texts_metadata_cache_key = _cache_key("Nautilus", "Inventory", "TextsMetadata", self.name)
        self.texts_parsed_cache_key = _cache_key("Nautilus", "Inventory", "TextsParsed", self.name)
        __inventory__ = self.__cache.get(self.inventory_cache_key)
        __texts__ = self.__cache.get(self.texts_metadata_cache_key)

        if __inventory__ and __texts__:
            self.inventory, self.__texts__ = __inventory__, __texts__
        elif auto_parse:
            self.parse(resource)

    def cache(self, inventory, texts):
        """ Cache main objects of the resolver : TextInventory and Texts Metadata objects

        :param inventory: Inventory resource
        :type inventory: TextInventory
        :param texts: List of Text Metadata Objects
        :type texts: [MyCapytain.resources.inventory.Text]
        """
        self.inventory, self.__texts__ = inventory, texts
        self.__cache.set(self.inventory_cache_key, inventory)
        self.__cache.set(self.texts_metadata_cache_key, texts)

    def flush(self):
        """ Flush current resolver objects and cache
        """
        self.inventory = TextInventory()
        self.__texts__ = []
        self.__cache.delete(self.inventory_cache_key)
        self.__cache.delete(self.texts_metadata_cache_key)

    def parse(self, resource, cache=True):
        """ Parse a list of directories ans

        :param resource: List of folders
        :param cache: Auto cache the results
        :return: An inventory resource and a list of Text metadata-objects
        """
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                try:
                    with io.open(__cts__) as __xml__:
                        textgroup = TextGroup(resource=__xml__)
                        textgroup.urn = URN(textgroup.xml.get("urn"))
                    self.inventory.textgroups[str(textgroup.urn)] = textgroup

                    for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                        with io.open(__subcts__) as __xml__:
                            work = Work(
                                resource=__xml__,
                                parents=[self.inventory.textgroups[str(textgroup.urn)]]
                            )
                            work.urn = URN(work.xml.get("urn"))
                            self.inventory.textgroups[str(textgroup.urn)].works[str(work.urn)] = work

                        for __textkey__ in self.inventory.textgroups[str(textgroup.urn)].works[str(work.urn)].texts:
                            __text__ = self.inventory.textgroups[str(textgroup.urn)].works[str(work.urn)].texts[__textkey__]
                            __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                                directory=os.path.dirname(__subcts__),
                                textgroup=__text__.urn.textgroup,
                                work=__text__.urn.work,
                                version=__text__.urn.version
                            )
                            if os.path.isfile(__text__.path):
                                try:
                                    with io.open(__text__.path) as f:
                                        t = Text(resource=f)
                                        cites = list()
                                        for cite in [c for c in t.citation][::-1]:
                                            if len(cites) >= 1:
                                                cites.append(Citation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name,
                                                    child=cites[-1]
                                                ))
                                            else:
                                                cites.append(Citation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name
                                                ))
                                    __text__.citation = cites[-1]
                                    self.logger.info("%s has been parsed ", __text__.path)
                                    if __text__.citation:
                                        self.__texts__.append(__text__)
                                    else:
                                        self.logger.error("%s has no passages", __text__.path)
                                except Exception:
                                    self.logger.error(
                                        "%s does not accept parsing at some level (most probably citation) ",
                                        __text__.path
                                    )
                            else:
                                self.logger.error("%s is not present", __text__.path)
                except Exception:
                    self.logger.error("Error parsing %s ", __cts__)

        if cache:
            self.cache(self.inventory, self.__texts__)

        return self.inventory, self.__texts__

    def getText(self, urn):
        """ Returns a Text object

        :param urn: URN of a text to retrieve
        :type urn: str, URN
        :return: Textual resource and metadata
        :rtype: (text.Text, inventory.Text)
        """
        if not isinstance(urn, URN):
            urn = URN(urn)
        if len(urn) != 5:
            raise InvalidURN

        text = self.inventory[str(urn)]
        with io.open(text.path) as __xml__:
            resource = self.TEXT_CLASS(urn=urn, resource=xmlparser(__xml__))

        return resource, text

    def getCapabilities(self,
            urn=None, page=None, limit=None,
            inventory=None, lang=None, category=None, pagination=True
        ):
        """ Retrieve a slice of the inventory filtered by given arguments

        :param urn: Partial URN to use to filter out resources
        :type urn: str
        :param page: Page to show
        :type page: int
        :param limit: Item Per Page
        :type limit: int
        :param inventory: Inventory name
        :type inventory: str
        :param lang: Language to filter on
        :type lang: str
        :param category: Type of elements to show
        :type category: str
        :param pagination: Activate pagination
        :type pagination: bool
        :return: ([Matches], Page, Count)
        :rtype: ([Text], int, int)
        """
        __PART = None
        if urn is not None:
            _urn = URN(urn)
            __PART = [None, None, URN.NAMESPACE, URN.TEXTGROUP, URN.WORK, URN.VERSION, URN.COMPLETE][len(_urn)]

        matches = [
            text
            for text in self.__texts__
            if (lang is None or (lang is not None and lang == text.lang)) and
            (urn is None or (urn is not None and text.urn.upTo(__PART) == urn)) and
            (text.citation is not None) and
            (category not in ["edition", "translation"] or (category in ["edition", "translation"] and category.lower() == text.subtype.lower()))
        ]
        if pagination:
            start_index, end_index, page, count = XMLFolderResolver.pagination(page, limit, len(matches))
        else:
            start_index, end_index, page, count = None, None, 0, len(matches)

        return matches[start_index:end_index], page, count
