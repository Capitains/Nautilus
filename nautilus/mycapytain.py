# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.common.reference import URN
from nautilus.inventory.local import XMLFolderResolver
from nautilus.response import *
from nautilus.errors import InvalidURN, UnknownResource


class NautilusEndpoint(CTS):
    """

    """
    def __init__(self, folders=[]):
        self.resolver = XMLFolderResolver(resource=folders)

    def getCapabilities(self, inventory=None, format=XML, **kwargs):
        """ Retrieve the inventory information of an API

        :param inventory: Name of the inventory
        :type inventory: text
        :param format:
        :type format:
        :return: Formatted output, according to format
        :rtype: str
        """
        return getcapabilities(*self.resolver.getCapabilities(inventory=inventory, **kwargs), format=format, **kwargs)

    def getPassage(self, urn, inventory=None, context=None, format=XML):
        """

        :param urn:
        :param inventory:
        :param context:
        :return:
        """
        original_urn, urn, _text, metadata = self.getText(urn, inventory)

        if format == MY_CAPYTAIN:
            return _text.getPassage(urn["reference"]), metadata
        else:
            return getpassage(_text.getPassage(urn["reference"]), metadata, original_urn, format=format)

    def getPassagePlus(self, urn, inventory=None, context=None, format=XML):
        """

        :param urn:
        :param inventory:
        :param context:
        :param format:
        :return:
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

    def getText(self, urn, inventory=None):
        """ Retrieves a text in the inventory in case of partial URN or throw error when text is not accessible

        :param urn:
        :param inventory:
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