# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type as str
from io import BytesIO

from capitains_nautilus.flask_ext import FlaskNautilus, FlaskNautilusManager, WerkzeugCacheWrapper
from werkzeug.contrib.cache import RedisCache, FileSystemCache
from flask import Flask
from flask_cache import Cache
from flask.ext.script import Manager
from unittest import TestCase
from MyCapytain.resources.inventory import TextInventory
from MyCapytain.resources.texts.api import Text, Passage
from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.reference import Reference


class TestRestAPI(TestCase):
    def setUp(self):
        nautilus_cache = WerkzeugCacheWrapper(RedisCache())
        app = Flask("Nautilus")
        nautilus = FlaskNautilus(
            app=app,
            resources=["./tests/test_data/latinLit"],
            parser_cache=nautilus_cache,
            http_cache=Cache(config={'CACHE_TYPE': 'redis'})
        )
        self.app = app.test_client()
        self.parent = CTS("/")

        def call(this, parameters={}):
            """ Call an endpoint given the parameters

            :param parameters: Dictionary of parameters
            :type parameters: dict
            :rtype: text
            """

            parameters = {
                key: str(parameters[key]) for key in parameters if parameters[key] is not None
            }
            if this.inventory is not None and "inv" not in parameters:
                parameters["inv"] = this.inventory

            request = self.app.get("/?{}".format(
                "&".join(
                    ["{}={}".format(key, value) for key, value in parameters.items()])
                )
            )
            return BytesIO(request.data)

        self.parent.call = lambda x: call(self.parent, x)

    def test_cors(self):
        """ Check that CORS enabling works """
        self.assertEqual(self.app.get("/?request=GetCapabilities").headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(self.app.get("/?request=GetCapabilities").headers["Access-Control-Allow-Methods"], "OPTIONS, GET")

    def test_restricted_cors(self):
        """ Check that area-restricted cors works """
        nautilus_cache = WerkzeugCacheWrapper(RedisCache())
        app = Flask("Nautilus")
        nautilus = FlaskNautilus(
            app=app,
            resources=["./tests/test_data/latinLit"],
            parser_cache=nautilus_cache,
            http_cache=Cache(config={'CACHE_TYPE': 'redis'}),
            access_Control_Allow_Methods={"r_dispatcher": "OPTIONS"},
            access_Control_Allow_Origin={"r_dispatcher": "foo.bar"}
        )
        _app = app.test_client()
        self.assertEqual(_app.get("/?request=GetCapabilities").headers["Access-Control-Allow-Origin"], "foo.bar")
        self.assertEqual(_app.get("/?request=GetCapabilities").headers["Access-Control-Allow-Methods"], "OPTIONS")

    def test_get_capabilities(self):
        """ Check the GetCapabilities request """
        response = self.app.get("/?request=GetCapabilities")
        a = TextInventory(resource=BytesIO(response.data))
        self.assertEqual(
            str(a["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
        )

    def test_get_passage(self):
        """ Check the GetPassage request """
        response = self.app.get("/?request=GetPassage&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        a = Passage(resource=xmlparser(BytesIO(response.data)), urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        self.assertEqual(
            a.text(), "Spero me secutum in libellis meis tale temperamen-"
        )

    def test_get_passage_plus(self):
        """ Check the GetPassagePlus request """
        text = Text(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.parent)
        response = text.getPassagePlus(Reference("1.pr.1"))
        self.assertEqual(
            response.text(), "Spero me secutum in libellis meis tale temperamen-"
        )
        self.assertEqual(
            response.prev, None
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.2"
        )

        response = text.getPassagePlus(Reference("1.pr.10"))
        self.assertEqual(
            response.text(), "borum veritatem, id est epigrammaton linguam, excu-",
            "Check Range works on normal middle GetPassage"
        )
        self.assertEqual(
            str(response.prev.reference), "1.pr.9"
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.11"
        )

        response = text.getPassagePlus(Reference("1.pr.10-1.pr.11"))
        self.assertEqual(
            response.text(), "borum veritatem, id est epigrammaton linguam, excu- "
                             "sarem, si meum esset exemplum: sic scribit Catullus, sic ",
            "Check Range works on GetPassagePlus"
        )
        self.assertEqual(
            str(response.prev.reference), "1.pr.8-1.pr.9",
            "Check Range works on GetPassagePlus and compute right prev"
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.12-1.pr.13",
            "Check Range works on GetPassagePlus and compute right next"
        )

    def test_get_prevnext_urn(self):
        """ Check the GetPrevNext request """
        text = Text(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.parent)
        prev, next = text.getPrevNextUrn(Reference("1.pr.1"))
        self.assertEqual(
            prev, None
        )
        self.assertEqual(
            str(next.reference), "1.pr.2"
        )

        response = text.getPassagePlus(Reference("1.pr.10"))
        self.assertEqual(
            str(response.prev.reference), "1.pr.9",
            "Check Range works on normal middle GetPassage"
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.11"
        )

        response = text.getPassagePlus(Reference("1.pr.10-1.pr.11"))
        self.assertEqual(
            str(response.prev.reference), "1.pr.8-1.pr.9",
            "Check Range works on GetPassagePlus and compute right prev"
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.12-1.pr.13",
            "Check Range works on GetPassagePlus and compute right next"
        )


class TestManager(TestCase):
    def setUp(self):
        """ Set up a dummy application with a manager """
        nautilus_cache = WerkzeugCacheWrapper(instance=FileSystemCache("cache_dir"))
        nautilus_cache.clear()
        app = Flask("Nautilus")
        nautilus = FlaskNautilus(
            app=app,
            resources=["./tests/test_data/latinLit"],
            parser_cache=nautilus_cache,
            http_cache=Cache(config={'CACHE_TYPE': 'redis'}),
            auto_parse=False
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