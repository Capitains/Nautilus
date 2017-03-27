from unittest import TestCase
from subprocess import call
from sys import executable
import os
import mock
import shutil
from tests.test_cli.config import subprocess_cache_dir
from tests.test_cli.app import resolver, nautilus_cache, http_cache


cwd = os.getcwd()
cwd = cwd.replace("tests/test_cli", "")
python = executable


class TestManager(TestCase):
    class ParsingCalled(Exception):
        pass

    def cli(self, *args):
        output = call([python, "./tests/test_cli/manager.py"] + list(args), cwd=cwd)
        if output != 0:
            raise Exception("Run failed")

    def setUp(self):
        self.cache = nautilus_cache
        self.resolver = resolver
        self.resolver.logger.disabled = True
        self.former_parse = self.resolver.parse

        def x(*k, **kw):
            raise TestManager.ParsingCalled("Parse should not be called")
        self.resolver.parse = x

    def tearDown(self):
        #shutil.rmtree(subprocess_cache_dir, ignore_errors=True)
        self.resolver.parse = self.former_parse

    def test_parse(self):
        self.cli("parse")
        self.assertEqual(len(self.resolver.texts), 2, "There should be 2 texts preprocessed")

    def test_flush_inventory(self):
        output = self.cli("parse")
        self.cli("flush_resolver")
        with self.assertRaises(TestManager.ParsingCalled):  # It is called because it will parse
            self.assertEqual(len(self.resolver.texts), 0, "There should be 0 texts preprocessed")

    def test_references(self):
        output = self.cli("parse")
        output_2 = self.cli("process_reffs")
        self.assertEqual(len(self.resolver.texts), 2, "There should be 2 texts preprocessed")
        with mock.patch("capitains_nautilus.cts.resolver.CTSCapitainsLocalResolver.getReffs") as getReffs:
            self.assertEqual(
                self.resolver.getReffs(textId=self.resolver.texts[0].id, level=2)[:5],
                ['1.pr', '1.1', '1.2', '1.3', '1.4']
            )
            getReffs.assert_not_called()
