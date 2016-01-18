from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.resources.texts.local import Text
from MyCapytain.common.reference import URN
from nautilus.inventory.local import XMLFolderResolver
from nautilus.response import *
from nautilus.errors import InvalidURN, UnknownResource

MY_CAPYTAIN = "MyCapytain"


class NautilusEndpoint(CTS):
    """

    """
    def __init__(self, folders=[]):
        self.resolver = XMLFolderResolver(resource=folders)

    def getCapabilities(self, inventory=None, format=XML, **kwargs):
        """

        :param inventory:
        :param format:
        :param kwargs:
        :return:
        """
        return capabilities(
            *self.resolver.getCapabilities(inventory=inventory, **kwargs),
            format=format,
            **kwargs
        )

    def getPassage(self, urn, inventory=None, context=None, format=XML):
        """

        :param urn:
        :param inventory:
        :param context:
        :return:
        """
        # If we don't have version
        original_urn = urn
        urn = URN(urn)
        if len(urn) == 4:
            matches, page, counter = self.resolver.getCapabilities(
                inventory=inventory, urn=urn["work"], category="edition"
            )
            if counter > 0:
                urn = URN("{0}:{1}".format(matches[0].urn, urn["reference"]))
            else:
                raise UnknownResource()
        elif len(urn) < 4:
            raise InvalidURN()

        _text, metadata = self.resolver.getText(urn["text"])

        # return passage_formatter()
        if format == MY_CAPYTAIN:
            return _text.getPassage(urn["reference"]), metadata
        else:
            return text(_text.getPassage(urn["reference"]), metadata, original_urn, format=format)
