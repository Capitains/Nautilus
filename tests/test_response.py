# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type as str

from unittest import TestCase
from nautilus.inventory.local import XMLFolderResolver
from nautilus.response import *
from MyCapytain.resources.inventory import TextInventory


class ResponseTest(TestCase):

    def setUp(self):
        self.inventory = XMLFolderResolver(["./tests/test_data/farsiLit"])

    def test_xml_capabilities(self):
        """ Check consistancy of XML response for Capabilites Response Maker """
        response = getcapabilities([
            self.inventory.resource["urn:cts:farsiLit:hafez.divan.perseus-eng1"],
            self.inventory.resource["urn:cts:farsiLit:hafez.divan.perseus-ger1"]
        ])
        ti = TextInventory(resource=response)
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan"].texts), 2,
            "Asserts that only two texts has been added to the TI"
        )
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan.perseus-eng1"].citation), 4
        )

    def test_with_get_capabilities(self):
        response = getcapabilities(*self.inventory.getCapabilities(category="translation"))
        ti = TextInventory(resource=response)
        self.assertEqual(
            len(ti["urn:cts:farsiLit:hafez.divan"].texts), 2,
            "Asserts that only two texts has been added to the TI"
        )