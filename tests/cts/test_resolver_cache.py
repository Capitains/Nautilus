from unittest import TestCase
from subprocess import call
from sys import executable
import os
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache
from MyCapytain.common.constants import Mimetypes
from tests.cts import subprocess_repository, subprocess_cache_dir

cwd = os.getcwd()
cwd = cwd.replace("tests/cts", "")
python = executable


class TestCache(TestCase):
    def setUp(self):
        output = call([python, "./tests/cts/run_cache.py"], cwd=cwd)
        if output != 0:
            raise Exception("Creating cache failed")

        self.cache = FileSystemCache(subprocess_cache_dir)
        self.resolver = NautilusCTSResolver(resource=subprocess_repository, cache=self.cache)

        def x(*k, **kw):
            raise Exception("Parse should not be called")
        self.resolver.parse = x

    def tearDown(self):
        self.cache.clear()

    def test_argumentless_metadata(self):
        inventory = self.resolver.getMetadata()

        self.assertIn(
            "Divān (English)",
            inventory.export(Mimetypes.XML.CTS),
            "Metadata are there"
        )
        self.assertEqual(
            len(inventory.readableDescendants), 4
        )

    def test_first_child(self):
        key = list(self.resolver.getMetadata().children.keys())[0]
        inventory = self.resolver.getMetadata(key)

        self.assertIn(
            "Divān (English)",
            inventory.export(Mimetypes.XML.CTS),
            "Metadata are there"
        )
        self.assertEqual(
            len(inventory.readableDescendants), 4
        )

    def test_textgroup(self):
        """ Found to fail originally because of different GRAPH constant used across modules
        (one from the cache vs. the world) """
        inventory = self.resolver.getMetadata("urn:cts:farsiLit:hafez")

        self.assertIn(
            "Divān (English)",
            inventory.export(Mimetypes.XML.CTS),
            "Metadata are there"
        )
        self.assertEqual(
            len(inventory.readableDescendants), 3
        )

