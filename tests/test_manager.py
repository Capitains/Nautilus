import logging
from unittest import TestCase
from flask import Flask
from flask_caching import Cache
from click.testing import CliRunner
from werkzeug.contrib.cache import FileSystemCache
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection as TextInventoryCollection

from capitains_nautilus.flask_ext import FlaskNautilus
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.manager import FlaskNautilusManager

# Clean up noise...
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger()

class TestManager(TestCase):
    CacheType, Cache_type_String = FileSystemCache, "filesystem"

    def setUp(self):
        """ Set up a dummy application with a manager """
        nautilus_cache = FileSystemCache("cache_dir")
        nautilus_cache.clear()
        app = Flask("Nautilus")
        resolver = NautilusCTSResolver(["./tests/test_data/latinLit"], cache=nautilus_cache, logger=logger)
        flask_nautilus = FlaskNautilus(
            app=app,
            resolver=resolver,
            flask_caching=Cache(config={'CACHE_TYPE': 'filesystem'}),
            logger=logger
        )
        self.cache_manager = nautilus_cache
        self.nautilus = flask_nautilus
        self.resolver = resolver
        self.resolver.logger.disabled = True
        self.manager = FlaskNautilusManager(resolver, flask_nautilus)

    def cmd(self, *args):
        runner = CliRunner()
        return runner.invoke(self.manager, list(args))

    def test_flush_cache(self):
        """ Simulate python manager.py
        """
        # Preparation : parsing resources, checking resources are there
        self.nautilus.resolver.parse(["./tests/test_data/latinLit"])
        self.assertEqual(len(self.resolver.texts) > 0, True,
                         "Texts should have been parsed")
        self.assertEqual(len(self.resolver.inventory) > 0, True,
                         "Inventory should have been parsed")
        self.assertEqual(
            len(self.cache_manager.get(self.resolver.inventory_cache_key)) > 0,
            True,
            "There should be inventory in cache"
        )

        # Running the tested command
        result = self.cmd("flush_resolver")
        # Fake new setup
        self.resolver.__texts__ = []
        self.resolver.__inventory__ = TextInventoryCollection("UNKNOWN")

        # Checking after state
        self.assertIs(
            self.cache_manager.get(self.resolver.inventory_cache_key), None,
            "There should not be inventory anymore in cache"
        )

    def test_process_cache(self):
        """ Simulate python manager.py
        """
        # Preparation : checking resources are not there
        self.assertEqual(len(self.resolver.inventory), 0, "Inventory should have been flushed")
        self.assertEqual(
            len(self.cache_manager.get(self.resolver.inventory_cache_key)),
            0,
            "There should not be inventory in cache"
        )

        # Running the tested command
        out = self.cmd("parse")
        self.assertIn("Preprocessed 2 texts", out.output)

        # Checking after state
        self.assertGreater(len(self.resolver.texts), 0, "Texts should have been parsed")
        self.assertGreater(len(self.resolver.inventory), 0, "Inventory should have been parsed")
        self.assertEqual(
            len(self.cache_manager.get(self.resolver.inventory_cache_key)) > 0,
            True,
            "There should be inventory in cache"
        )
