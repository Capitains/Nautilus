# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type as str
from io import BytesIO

from nautilus.flask_ext import FlaskNautilus
from werkzeug.contrib.cache import RedisCache
from flask import Flask
from flask_cache import Cache
from unittest import TestCase
from MyCapytain.resources.inventory import TextInventory
from MyCapytain.resources.texts.api import Text, Passage
from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.reference import Reference


class TestRestAPI(TestCase):
    def setUp(self):
        nautilus_cache = RedisCache()
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


    def test_get_capabilities(self):
        response = self.app.get("/?request=GetCapabilities")
        a = TextInventory(resource=BytesIO(response.data))
        self.assertEqual(
            str(a["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
        )

    def test_get_passage(self):
        response = self.app.get("/?request=GetPassage&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        a = Passage(resource=xmlparser(BytesIO(response.data)), urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        self.assertEqual(
            a.text(), "Spero me secutum in libellis meis tale temperamen-"
        )

    def test_get_passage_plus(self):
        text = Text(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.parent)
        response = text.getPassagePlus(Reference("1.pr.1"))
        self.assertEqual(
            response.text(), "Spero me secutum in libellis meis tale temperamen-"
        )
        self.assertEqual(
            response._prev, None
        )
        self.assertEqual(
            str(response._next.reference), "1.pr.2"
        )

        response = text.getPassagePlus(Reference("1.pr.10"))
        self.assertEqual(
            response.text(), "borum veritatem, id est epigrammaton linguam, excu-",
            "Check Range works on normal middle GetPassage"
        )
        self.assertEqual(
            str(response._prev.reference), "1.pr.9"
        )
        self.assertEqual(
            str(response._next.reference), "1.pr.11"
        )

        response = text.getPassagePlus(Reference("1.pr.10-1.pr.11"))
        self.assertEqual(
            response.text(), "borum veritatem, id est epigrammaton linguam, excu- "
                             "sarem, si meum esset exemplum: sic scribit Catullus, sic ",
            "Check Range works on GetPassagePlus"
        )
        self.assertEqual(
            str(response._prev.reference), "1.pr.8-1.pr.9",
            "Check Range works on GetPassagePlus and compute right prev"
        )
        self.assertEqual(
            str(response._next.reference), "1.pr.12-1.pr.13",
            "Check Range works on GetPassagePlus and compute right next"
        )