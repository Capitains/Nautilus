from unittest import TestCase
from lilacs.inventory.local import XMLFolderResolver
from lilacs.response import *
from MyCapytain.resources.inventory import TextInventory


class ResponseTest(TestCase):

    def setUp(self):
        self.inventory = XMLFolderResolver(["./tests/test_data/farsiLit"])

    def test_xml_capabilities(self):
        """ Check consistancy of XML response for Capabilites Response Maker """
        response = capabilities([
            self.inventory.resource["urn:cts:farsiLit:hafez.divan.perseus-eng1"],
            self.inventory.resource["urn:cts:farsiLit:hafez.divan.perseus-ger1"]
        ])
        ti = TextInventory(resource=response)
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan"].texts), 2,
            "Asserts that only two texts has been added to the TI"
        )