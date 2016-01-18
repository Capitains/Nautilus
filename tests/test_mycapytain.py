from nautilus.mycapytain import NautilusEndpoint, MY_CAPYTAIN
from MyCapytain.resources.inventory import TextInventory
from unittest import TestCase


class ResponseTest(TestCase):

    def setUp(self):
        self.endpoint = NautilusEndpoint(["./tests/test_data/farsiLit"])

    def test_with_get_capabilities(self):
        response = self.endpoint.getCapabilities(category="translation")
        ti = TextInventory(resource=response)
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan"].texts), 2,
            "Asserts that only two texts has been added to the TI"
        )

    def test_get_passage_complete_urn(self):
        """ Test Get Passage """
        response, metadata = self.endpoint.getPassage("urn:cts:farsiLit:hafez.divan.perseus-eng1:1.1.1.1", format=MY_CAPYTAIN)
        self.assertEqual(
            response.text(),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )

    def test_get_passage_partial_urn(self):
        """ Test Get Passage """
        response, metadata = self.endpoint.getPassage("urn:cts:farsiLit:hafez.divan:1.1.1.1", format=MY_CAPYTAIN)
        self.assertEqual(
            response.text(),
            "الا یا ایها الساقی ادر کاسا و ناولها ### ",
            "It should be possible to retrieve text from edition without veersion"
        )