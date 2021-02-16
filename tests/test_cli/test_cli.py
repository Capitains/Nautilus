from unittest import TestCase
from subprocess import call
from sys import executable
import glob
import os
import mock
import shutil
from click.testing import CliRunner
from capitains_nautilus.manager import FlaskNautilusManager
from tests.test_cli.config import subprocess_cache_dir, http_cache_dir, subprocess_repository
from tests.test_cli.app import resolver, nautilus_cache, make_dispatcher, app, nautilus
from flask import Flask
from flask_caching import Cache
from cachelib import FileSystemCache
from capitains_nautilus.cts.resolver import NautilusCtsResolver
from capitains_nautilus.flask_ext import FlaskNautilus


from MyCapytain.common.reference import CtsReference, CtsReferenceSet


cwd = os.getcwd()
cwd = cwd.replace("tests/test_cli", "")
python = executable


class TestManager(TestCase):
    """ Test the manager ability to preprocess and cache some resources

    .. note:: FileSystemCache leaves a cache file to indicate the number of other cache files . More in
    https://github.com/Capitains/Nautilus/issues/62 and https://github.com/pallets/werkzeug/blob/8393ee88aaacf7bcd3a0b1d604511f70c222df25/werkzeug/contrib/cache.py#L773-L781
    """

    @property
    def app(self):
        return self.__app__

    class ParsingCalled(Exception):
        pass

    def cli(self, *args):
        output = call([python, "./tests/test_cli/manager.py"] + list(args), cwd=cwd)
        if output != 0:
            raise Exception("Run failed")

    def setUp(self):
        shutil.rmtree(subprocess_cache_dir, ignore_errors=True)
        shutil.rmtree(http_cache_dir, ignore_errors=True)
        self.cache = nautilus_cache
        self.resolver = resolver
        self.resolver.dispatcher = make_dispatcher()
        self.resolver.__inventory__ = None
        self.resolver.logger.disabled = True
        self.former_parse = self.resolver.parse
        self.nautilus = nautilus
        self.__app__ = app
        self.nautilus.flaskcache.init_app(self.app)
        self.test_client = self.app.test_client()

        def x(*k, **kw):
            raise self.ParsingCalled("Parse should not be called")
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
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertGreater(len(files), 1, "There should be caching operated by resolver")
        self.cli("flush_resolver")
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertEqual(len(files), 1, "Resolver Cache should be flushed (and only the count cache file should remain")

    def test_flush_http(self):
        """ Check that parsing works, that flushing removes the http cache """
        self.cli("parse")

        response = self.test_client.get("/api/cts?request=GetCapabilities")
        self.assertIn(
            '<label xml:lang="eng">Epigrammata</label>', response.data.decode(),
            "Response should be correctly produced"
        )

        files = glob.glob(http_cache_dir+"/*")
        self.assertGreater(len(files), 1, "There should be caching operated by flask-caching")

        self.cli("flush_http_cache")
        files = glob.glob(http_cache_dir+"/*")
        self.assertEqual(len(files), 1, "HTTP Cache should be flushed (and only the count cache file should remain")

        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertGreater(len(files), 1, "But not of Resolver Cache")

    def test_flush_both(self):
        """ Check that parsing works, that both flushing removes the http cache and resolver cache"""
        self.cli("parse")

        response = self.test_client.get("/api/cts?request=GetCapabilities")
        self.assertIn(
            '<label xml:lang="eng">Epigrammata</label>', response.data.decode(),
            "Response should be correctly produced"
        )

        files = glob.glob(http_cache_dir+"/*")
        self.assertGreater(len(files), 1, "There should be caching operated by flask-caching")
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertGreater(len(files), 1, "There should be caching operated by resolver")

        self.cli("flush_both")
        files = glob.glob(http_cache_dir+"/*")
        self.assertEqual(len(files), 1, "HTTP Cache should be flushed (and only the count cache file should remain")
        files = glob.glob(subprocess_cache_dir+"/*")
        self.assertEqual(len(files), 1, "Resolver Cache should be flushed (and only the count cache file should remain")

    def test_references(self):
        output = self.cli("parse")
        output_2 = self.cli("process_reffs")
        self.assertEqual(len(self.resolver.texts), 2, "There should be 2 texts preprocessed")
        with mock.patch("capitains_nautilus.cts.resolver.base.CtsCapitainsLocalResolver.getReffs") as getReffs:
            self.assertEqual(
                self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)[:5],
                CtsReferenceSet([CtsReference('1.pr'), CtsReference('1.1'), CtsReference('1.2'), CtsReference('1.3'),
                 CtsReference('1.4')])
            )
            getReffs.assert_not_called()


class TestManagerClickMethod(TestManager):
    """ Rerun the same tests but in the context of unit test """

    def setUp(self):
        # Full creation of app
        self.cache = FileSystemCache(subprocess_cache_dir, default_timeout=0)
        self.resolver = NautilusCtsResolver(
            subprocess_repository,
            dispatcher=make_dispatcher(),
            cache=self.cache
        )
        self.__app__ = Flask("Nautilus")
        self.http_cache = Cache(
            self.app,
            config={
                'CACHE_TYPE': "filesystem",
                "CACHE_DIR": http_cache_dir,
                "CACHE_DEFAULT_TIMEOUT": 0
            }
        )
        self.nautilus = FlaskNautilus(
            app=self.app,
            prefix="/api",
            name="nautilus",
            resolver=self.resolver,
            flask_caching=self.http_cache
        )

        self.test_client = self.app.test_client()

        # Option to ensure cache works
        self.former_parse = self.resolver.parse

        def x(*k, **kw):
            raise self.ParsingCalled("Parse should not be called")
        self.resolver.parse = x

    def cli(self, *args):
        """ Run command using CliRunner

        :param args:
        :return:
        """
        manager = FlaskNautilusManager(self.resolver, self.nautilus)
        runner = CliRunner()
        raising_parse = self.resolver.parse
        # Ensure Parsing can work
        self.resolver.parse = self.former_parse
        invoked = runner.invoke(manager, list(args))
        self.resolver.parse = raising_parse
        self.__inventory__ = None
        return invoked
