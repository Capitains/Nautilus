from MyCapytain.resources.inventory import TextInventory, TextGroup, Work
from MyCapytain.resources.texts.local import Text
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import xmlparser
from lilacs.errors import *
from glob import glob
import os.path
from lilacs.inventory.proto import InventoryResolver


class XMLFolderResolver(InventoryResolver):
    """ XML Folder Based resolver.

     .. warning :: This resolver does not support inventories
     """
    def __init__(self, resource, cache_folder="./cache"):
        """ Initiate the XMLResolver

        :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
        :type resource: [str]
        """
        super(XMLFolderResolver, self).__init__(resource=TextInventory())

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
            resource = Text(urn=urn, resource=xmlparser(__xml__))

        return resource, text

    def getCapabilities(self, urn=None, page=None, limit=None, inventory=None, lang=None, category=None):
        """

        :param urn:
        :param page:
        :param limit:
        :param inventory:
        :param lang:
        :param category:
        :return: ([Matches], Page, Count)
        """
        matches = [
            text
            for text in self.__texts__
            if (lang is None or (lang is not None and lang == text.lang)) and
            (category is None or (category is not None and category.lower() == text.subtype.lower()))
        ]
        start_index, end_index, page, count = XMLFolderResolver.pagination(page, limit, len(matches))

        return matches[start_index:end_index], page, count