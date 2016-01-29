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

    def test_get_capabilities(self):
        response = self.app.get("/?request=GetCapabilities")
        a = TextInventory(resource=BytesIO(response.data))
        self.assertEqual(
            str(a["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
        )