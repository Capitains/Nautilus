# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type as str
from io import open

from MyCapytain.resources.inventory import TextInventory, TextGroup, Work
from MyCapytain.resources.texts.local import Text
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import xmlparser
from nautilus.errors import *
from glob import glob
import os.path
from nautilus.inventory.proto import InventoryResolver


class XMLFolderResolver(InventoryResolver):
    """ XML Folder Based resolver.

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]

    .. warning :: This resolver does not support inventories
    """
    TEXT_CLASS = Text


    def __init__(self, resource):
        """ Initiate the XMLResolver
        """
        super(XMLFolderResolver, self).__init__(resource=TextInventory())

        self.TEXT_CLASS = XMLFolderResolver.TEXT_CLASS
        self.works = []
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                with open(__cts__) as __xml__:
                    textgroup = TextGroup(resource=__xml__)
                    textgroup.urn = URN(textgroup.xml.get("urn"))
                self.resource.textgroups[str(textgroup.urn)] = textgroup

                for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                    with open(__subcts__) as __xml__:
                        work = Work(
                            resource=__xml__,
                            parents=tuple([self.resource.textgroups[str(textgroup.urn)]])
                        )
                        work.urn = URN(work.xml.get("urn"))
                    self.resource.textgroups[str(textgroup.urn)].works[str(work.urn)] = work

                    for __text__ in self.resource.textgroups[str(textgroup.urn)].works[str(work.urn)].texts.values():
                        __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                            directory=os.path.dirname(__subcts__),
                            textgroup=__text__.urn[3],
                            work=__text__.urn[4],
                            version=__text__.urn[5]
                        )
                        self.__texts__.append(__text__)

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

        text = self.resource[str(urn)]
        with open(text.path) as __xml__:
            resource = self.TEXT_CLASS(urn=urn, resource=xmlparser(__xml__))

        return resource, text

    def getCapabilities(self, urn=None, page=None, limit=None, inventory=None, lang=None, category=None):
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
        :return: ([Matches], Page, Count)
        :rtype: ([Text], int, int)
        """
        urn_part = None
        if urn is not None:
            _urn = URN(urn)
            urn_part = ["full", "urn_namespace", "cts_namespace", "textgroup", "work", "text", "full"][len(_urn)]

        matches = [
            text
            for text in self.__texts__
            if (lang is None or (lang is not None and lang == text.lang)) and
            (urn is None or (urn is not None and text.urn[urn_part] == urn)) and
            (category not in ["edition", "translation"] or (category in ["edition", "translation"] and category.lower() == text.subtype.lower()))
        ]
        start_index, end_index, page, count = XMLFolderResolver.pagination(page, limit, len(matches))

        return matches[start_index:end_index], page, count
