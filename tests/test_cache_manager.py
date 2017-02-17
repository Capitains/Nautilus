# -*- coding: utf-8 -*-

from capitains_nautilus.flask_ext import FlaskNautilus, FlaskNautilusManager, WerkzeugCacheWrapper
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import RedisCache, FileSystemCache
from flask import Flask
from flask.ext.script import Manager
from unittest import TestCase
import logging

# Clean up noise...
logging.basicConfig(level=logging.CRITICAL)


class TestManager(TestCase):
    def setUp(self):
        """ Set up a dummy application with a manager """
        nautilus_cache = WerkzeugCacheWrapper(instance=FileSystemCache("cache_dir"))
        nautilus_cache.clear()
        app = Flask("Nautilus")
        nautilus = FlaskNautilus(
            app=app,
            resolver=NautilusCTSResolver(["./tests/test_data/latinLit"]),
            #http_cache=Cache(config={'CACHE_TYPE': 'redis'}),
        )
        self.cache_manager = nautilus_cache
        self.nautilus = nautilus
        self.manager = Manager(app)
        self.manager.add_command("nautilus", FlaskNautilusManager(nautilus, app=app))

    def test_flush_cache(self):
        """ Simulate python manager.py
        """
        # Preparation : parsing resources, checking resources are there
        self.nautilus.retriever.resolver.parse(["./tests/test_data/latinLit"])
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) > 0, True,
                         "Texts should have been parsed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) > 0, True,
                         "Inventory should have been parsed")
        self.assertEqual(
            len(self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key)) > 0,
            True,
            "There should be inventory in cache"
        )

        # Running the tested command
        self.manager.handle("", ["nautilus", "flush"])

        # Checking after state
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) == 0, True, "Texts should have been flushed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) == 0, True, "Inventory should have been flushed")
        self.assertEqual(
            self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key) is None,
            True,
            "There should not be inventory anymore in cache"
        )

    def test_process_cache(self):
        """ Simulate python manager.py
        """
        # Preparation : checking resources are not there
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) == 0, True, "Texts should have been flushed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) == 0, True, "Inventory should have been flushed")
        self.assertEqual(
            self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key) is None,
            True,
            "There should not be inventory in cache"
        )
        self.assertEqual(
            self.cache_manager.get(self.nautilus.retriever.resolver.texts_metadata_cache_key) is None,
            True,
            "There should not be texts metadata in cache"
        )

        # Running the tested command
        self.manager.handle("", ["nautilus", "preprocess"])

        # Checking after state
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) > 0, True,
                         "Texts should have been parsed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) > 0, True,
                         "Inventory should have been parsed")
        self.assertEqual(
            len(self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key)) > 0,
            True,
            "There should be inventory in cache"
        )
        self.assertEqual(
            len(self.cache_manager.get(self.nautilus.retriever.resolver.texts_metadata_cache_key)) > 0,
            True,
            "There should be texts metadata in cache"
        )

    def test_rebuild_inventory_cache(self):
        """ Simulate python manager.py
        """
        # Preparation : checking resources are not there
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) == 0, True, "Texts should have been flushed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) == 0, True, "Inventory should have been flushed")
        self.assertEqual(
            self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key) is None,
            True,
            "There should not be inventory in cache"
        )
        self.assertEqual(
            self.cache_manager.get(self.nautilus.retriever.resolver.texts_metadata_cache_key) is None,
            True,
            "There should not be texts metadata in cache"
        )

        # Running the tested command
        self.manager.handle("", ["nautilus", "inventory"])

        # Checking after state
        self.assertEqual(len(self.nautilus.retriever.resolver.texts) > 0, True,
                         "Texts should have been parsed")
        self.assertEqual(len(self.nautilus.retriever.resolver.inventory) > 0, True,
                         "Inventory should have been parsed")
        self.assertEqual(
            len(self.cache_manager.get(self.nautilus.retriever.resolver.inventory_cache_key)) > 0,
            True,
            "There should be inventory in cache"
        )
        self.assertEqual(
            len(self.cache_manager.get(self.nautilus.retriever.resolver.texts_metadata_cache_key)) > 0,
            True,
            "There should be texts metadata in cache"
        )