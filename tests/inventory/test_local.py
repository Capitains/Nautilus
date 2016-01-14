from lilacs.inventory.local import XMLFolderResolver
from MyCapytain.common.reference import URN, Reference
from unittest import TestCase


class TestXMLFolderResolver(TestCase):
    def test_resource_parser(self):
        """ Test that the initiation finds correctly the resources """
        Repository = XMLFolderResolver(["./tests/test_data/farsiLit"])
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

    def test_text_resource(self):
        """ Test to get the text resource to perform other queries """
        Repository = XMLFolderResolver(["./tests/test_data/farsiLit"])
        text, metadata = Repository.getText("urn:cts:farsiLit:hafez.divan.perseus-eng1")
        self.assertEqual(
            len(text.citation), 4,
            "Object has a citation property of length 4"
        )
        self.assertEqual(
            text.getPassage(Reference("1.1.1.1")).text(),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )