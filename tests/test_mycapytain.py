# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type as str

from nautilus.mycapytain import NautilusEndpoint, MY_CAPYTAIN, XML

from MyCapytain.resources.inventory import TextInventory
from MyCapytain.resources.texts.api import Passage
from MyCapytain.common.utils import xmlparser
from unittest import TestCase


class ResponseTest(TestCase):

    def setUp(self):
        self.endpoint = NautilusEndpoint(["./tests/test_data/farsiLit"])

    def test_with_get_capabilities(self):
        response = self.endpoint.getCapabilities(category="translation", format=MY_CAPYTAIN)
        ti = TextInventory(resource=response)
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan"].texts), 2,
            "Asserts that only two texts has been added to the TI"
        )

    def test_with_get_capabilities_cts_response(self):
        response = self.endpoint.getCapabilities(category="translation", format=XML)
        self.assertIn(
            "<requestFilters>category=translation</requestFilters>", response,
            "Filters should be listed"
        )
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
            "It should be possible to retrieve text from edition without version"
        )

    def test_get_passage_formatted(self):
        response = self.endpoint.getPassage("urn:cts:farsiLit:hafez.divan:1.1.1.1", format=XML)
        p = Passage(resource=xmlparser(response), urn="urn:cts:farsiLit:hafez.divan:1.1.1.1")
        """
        self.assertEqual(
            p.text(),
            "الا یا ایها الساقی ادر کاسا و ناولها ###",
            "API Response should be parsable by MyCapytain Library"
        )
        """

    def test_get_passage_plus_formatted(self):
        response = self.endpoint.getPassagePlus("urn:cts:farsiLit:hafez.divan:1.1.1.2", format=XML)
        parsed_response = Passage(resource=xmlparser(response), urn="urn:cts:farsiLit:hafez.divan:1.1.1.2")
        self.assertEqual(
            parsed_response.text().strip(),
            "که عشق آسان نمود اول ولی افتاد مشکل‌ها ***",
            "API Response should be parsable by MyCapytain Library"
        )
        self.assertIn(
            "<prev><urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1.1.1</urn></prev>", response,
            "Previous URN should be found"
        )
        self.assertIn(
            "<next><urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1.2.1</urn></next>", response,
            "Next URN should be found"
        )

    def test_get_valid_reff(self):
        """ With reference """
        response = self.endpoint.getValidReff("urn:cts:farsiLit:hafez.divan:1.1", format=XML)
        self.assertIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1.1</urn>", response,
            "First URN should be found"
        )
        self.assertNotIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.2.1</urn>", response,
            "First URN should be found"
        )

    def test_get_valid_reff_simple(self):
        """ Without reference """
        response = self.endpoint.getValidReff("urn:cts:farsiLit:hafez.divan", format=XML)
        self.assertIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1</urn>", response,
            "First URN should be found"
        )
        self.assertNotIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1</urn>", response,
            "First URN should be found"
        )

        response = self.endpoint.getValidReff("urn:cts:farsiLit:hafez.divan", level=4, format=XML)
        self.assertIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1.1.2</urn>", response,
            "First URN should be found"
        )
        self.assertNotIn(
            "<urn>urn:cts:farsiLit:hafez.divan.perseus-far1:1.1</urn>", response,
            "First URN should be found"
        )
