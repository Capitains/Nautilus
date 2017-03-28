from unittest import TestCase
from subprocess import call
from sys import executable
import glob
import os
import mock
import shutil
from tests.test_cli.config import subprocess_cache_dir, http_cache_dir
from tests.test_cli.app import resolver, nautilus_cache, make_dispatcher, app, nautilus


cwd = os.getcwd()
cwd = cwd.replace("tests/test_cli", "")
python = executable


class TestManager(TestCase):

    class ParsingCalled(Exception):
        pass

    class GetCapabilitiesCalledException(Exception):
        pass

    def cli(self, *args):
        output = call([python, "./tests/test_cli/manager.py"] + list(args), cwd=cwd)
        if output != 0:
            raise Exception("Run failed")

    def setUp(self):
        self.cache = nautilus_cache
        self.resolver = resolver
        self.resolver.dispatcher = make_dispatcher()
        self.resolver.__inventory__ = None
        self.resolver.logger.disabled = True
        self.former_parse = self.resolver.parse
        self.nautilus = nautilus
        self.client = app.test_client()

        def x(*k, **kw):
            raise TestManager.ParsingCalled("Parse should not be called")
        self.resolver.parse = x

    def tearDown(self):
        shutil.rmtree(subprocess_cache_dir, ignore_errors=True)
        shutil.rmtree(http_cache_dir, ignore_errors=True)
        self.resolver.parse = self.former_parse

    def test_parse(self):
        """ Check that parsing works """
        self.cli("parse")
        self.assertEqual(len(self.resolver.texts), 2, "There should be 2 texts preprocessed")

    def test_flush_inventory(self):
        """ Check that parsing works and that flushing removes the cache """
        self.cli("parse")
        self.cli("flush_resolver")
        with self.assertRaises(TestManager.ParsingCalled):  # It is called because it will parse
            self.resolver.inventory

    def test_flush_http(self):
        """ Check that parsing works, that flushing removes the http cache """
        self.cli("parse")

        with app.app_context():
            x = nautilus._r_GetCapabilities()
            self.assertIn(
                '<label xml:lang="eng">Epigrammata</label>', x[0],
                "Response should be correctly produced"
            )

        files = glob.glob(http_cache_dir+"/*")
        self.assertGreater(len(files), 0, "There should be caching operated by flask-caching")

        self.cli("flush_http_cache")
        files = glob.glob(http_cache_dir+"/*")
        self.assertEqual(len(files), 0, "There should be flushing of flask-caching")

        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertGreater(len(files), 0, "But not of Resolver Cache")

    def test_flush_both(self):
        """ Check that parsing works, that both flushing removes the http cache and resolver cache"""
        self.cli("parse")

        with app.app_context():
            x = nautilus._r_GetCapabilities()
            self.assertIn(
                '<label xml:lang="eng">Epigrammata</label>', x[0],
                "Response should be correctly produced"
            )

        files = glob.glob(http_cache_dir+"/*")
        self.assertGreater(len(files), 0, "There should be caching operated by flask-caching")
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertGreater(len(files), 0, "There should be caching operated by resolver")

        self.cli("flush_both")
        files = glob.glob(http_cache_dir+"/*")
        self.assertEqual(len(files), 0, "There should be flushing of flask-caching")
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertEqual(len(files), 0, "There should be flushing of resolver")

    def test_references(self):
        output = self.cli("parse")
        output_2 = self.cli("process_reffs")
        self.assertEqual(len(self.resolver.texts), 2, "There should be 2 texts preprocessed")
        with mock.patch("capitains_nautilus.cts.resolver.CTSCapitainsLocalResolver.getReffs") as getReffs:
            self.assertEqual(
                self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)[:5],
                ['1.pr', '1.1', '1.2', '1.3', '1.4']
            )
            getReffs.assert_not_called()
