from nautilus.inventory.local import XMLFolderResolver
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

    def test_get_capabilities(self):
        """ Check Get Capabilities """
        Repository = XMLFolderResolver(
            ["./tests/test_data/farsiLit"]
        )
        self.assertEqual(
            len(Repository.getCapabilities()[0]), 3,
            "General no filter works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(category="edition")[0]), 1,
            "Type filter works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(lang="ger")[0]), 1,
            "Filtering on language works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(category="edition", lang="ger")[0]), 0,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(category="translation", lang="ger")[0]), 1,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(page=1, limit=2)[0]), 2,
            "Pagination works without other filters"
        )
        self.assertEqual(
            len(Repository.getCapabilities(page=2, limit=2)[0]), 1,
            "Pagination works without other filters at list end"
        )
        self.assertEqual(
            len(Repository.getCapabilities(urn="urn:cts:farsiLit")[0]), 3,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.getCapabilities(urn="urn:cts:farsiLit:hafez.divan.perseus-eng1")[0]), 1,
            "Complete URN filtering works"
        )