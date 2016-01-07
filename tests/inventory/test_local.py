from lilacs.inventory.local import XMLFolderResolver
from MyCapytain.common.reference import URN
from unittest import TestCase


class TestXMLFolderResolver(TestCase):
    def test_resource_parser(self):
        """ Test that the initiation finds correctly the resources """
        Repository = XMLFolderResolver(["../test_data/farsiLit"])
        self.assertEqual(
            Repository.resource["urn:cts:farsiLit:hafez"].urn, URN("urn:cts:farsiLit:hafez"),
            "Hafez is found"
        )
        self.assertEqual(
            len(Repository.resource["urn:cts:farsiLit:hafez"].works), 1,
            "Hafez has one child"
        )
        self.assertEqual(
            Repository.resource["urn:cts:farsiLit:hafez.divan"].urn, URN("urn:cts:farsiLit:hafez.divan"),
            "Divan is found"
        )
        self.assertEqual(
            len(Repository.resource["urn:cts:farsiLit:hafez.divan"].texts), 3,
            "Divan has 3 children"
        )