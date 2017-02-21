from unittest import TestCase
from flask import Flask
from flask_caching import Cache
from werkzeug.contrib.cache import RedisCache
import json

from capitains_nautilus.flask_ext import FlaskNautilus
from capitains_nautilus.cts.resolver import NautilusCTSResolver

from MyCapytain.resources.collections.cts import TextInventory, Citation
from MyCapytain.resources.texts.api.cts import Text
from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.resolvers.cts.api import HttpCTSResolver
from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.common.reference import Reference
from MyCapytain.common.constants import Mimetypes
from lxml.etree import tostring
import re
import logging
from logassert import logassert

# Clean up noise...
logging.basicConfig(level=logging.CRITICAL)


class TestRestAPI(TestCase):
    def setUp(self):
        app = Flask("Nautilus")
        nauti = FlaskNautilus(
            app=app,
            resolver=NautilusCTSResolver(["./tests/test_data/latinLit"])
        )
        app.debug = True
        self.cache = None
        self.app = app.test_client()
        self.parent = CTS("/cts")
        self.resolver = HttpCTSResolver(endpoint=self.parent)
        logassert.setup(self, nauti.logger.name)

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

            request = self.app.get("/cts?{}".format(
                "&".join(
                    ["{}={}".format(key, value) for key, value in parameters.items()])
                )
            )
            self.parent.called.append(parameters)
            return request.data.decode()

        self.parent.called = []
        self.parent.call = lambda x: call(self.parent, x)

    def test_cors(self):
        """ Check that CORS enabling works """
        self.assertEqual(self.app.get("/cts?request=GetCapabilities").headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(self.app.get("/cts?request=GetCapabilities").headers["Access-Control-Allow-Methods"], "OPTIONS, GET")

    def test_restricted_cors(self):
        """ Check that area-restricted cors works """
        app = Flask("Nautilus")
        FlaskNautilus(
            app=app,
            resolver=NautilusCTSResolver(["./tests/test_data/latinLit"]),
            access_Control_Allow_Methods={"r_cts": "OPTIONS", "r_dts_collection": "OPTIONS", "r_dts_collections": "OPTIONS"},
            access_Control_Allow_Origin={"r_cts": "foo.bar", "r_dts_collection":"*", "r_dts_collections":"*"}
        )
        _app = app.test_client()
        self.assertEqual(_app.get("/cts?request=GetCapabilities").headers["Access-Control-Allow-Origin"], "foo.bar")
        self.assertEqual(_app.get("/cts?request=GetCapabilities").headers["Access-Control-Allow-Methods"], "OPTIONS")

    def test_get_capabilities(self):
        """ Check the GetCapabilities request """
        response = self.app.get("/cts?request=GetCapabilities")
        a = TextInventory.parse(resource=response.data.decode())
        self.assertEqual(
            str(a["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
        )
        # Test for cache : only works in Cache situation, with specific SIMPLE BACKEND
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_partial_capabilities(self):
        response = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(
            response.id, "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_get_passage(self):
        """ Check the GetPassage request """
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.pr.1")
        self.assertEqual(
            passage.export(Mimetypes.PLAINTEXT), "Spero me secutum in libellis meis tale temperamen-"
        )
        self.assertCountEqual(
            self.parent.called, [{"request": "GetPassage", "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"}]
        )
        p, n = passage.siblingsId
        self.assertEqual((None, "1.pr.2"), (p, n), "Passage range should be given")
        self.assertCountEqual(
            self.parent.called,
            [
                {"request": "GetPassage", "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"},
                {"request": "GetPrevNextUrn", "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"}
            ]
        )
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_get_valid_reff(self):
        passages = self.resolver.getReffs("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.pr")
        self.assertEqual(
            passages, [
                "1.pr.1", '1.pr.2', '1.pr.3', '1.pr.4', '1.pr.5', '1.pr.6', '1.pr.7', '1.pr.8', '1.pr.9', '1.pr.10',
                '1.pr.11', '1.pr.12', '1.pr.13', '1.pr.14', '1.pr.15', '1.pr.16', '1.pr.17', '1.pr.18', '1.pr.19',
                '1.pr.20', '1.pr.21', '1.pr.22'
            ]
        )
        self.assertCountEqual(
            self.parent.called, [{
                "request": "GetValidReff", "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr", "level":"1"
            }]
        )
        passages = self.resolver.getReffs(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            subreference="1.pr.1-1.pr.5",
            level=0
        )
        self.assertEqual(
            passages, [
                "1.pr.1", '1.pr.2', '1.pr.3', '1.pr.4', '1.pr.5'
            ]
        )
        self.assertCountEqual(
            self.parent.called, [{
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr",
                "level": "1"
            },{
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1-1.pr.5",
                "level": "0"
            }]
        )
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_get_passage_plus(self):
        """ Check the GetPassagePlus request """
        response = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.pr.1",
            prevnext=True, metadata=True
        )
        self.assertEqual(
            response.export(Mimetypes.PLAINTEXT), "Spero me secutum in libellis meis tale temperamen-"
        )
        self.assertEqual(
            response.prev, None
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.2"
        )

        response = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.pr.10",
            prevnext=True, metadata=True
        )
        self.assertEqual(
            response.export(Mimetypes.PLAINTEXT), "borum veritatem, id est epigrammaton linguam, excu-",
            "Check Range works on normal middle GetPassage"
        )
        self.assertEqual(
            str(response.prev.reference), "1.pr.9"
        )
        self.assertEqual(
            str(response.next.reference), "1.pr.11"
        )

        response = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.pr.10-1.pr.11",
            prevnext=True, metadata=True
        )
        self.assertEqual(
            response.export(Mimetypes.PLAINTEXT), "borum veritatem, id est epigrammaton linguam, excu- "
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
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_get_prevnext_urn(self):
        """ Check the GetPrevNext request """
        text = Text(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.parent)
        p, n = text.getPrevNextUrn(Reference("1.pr.1"))
        self.assertEqual(
            p, None
        )
        self.assertEqual(
            n, "1.pr.2"
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
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_get_label(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = self.app.get("/cts?request=GetLabel&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2")\
            .data.decode("utf-8").replace("\n", "")
        parsed = xmlparser(data)
        label = parsed.xpath(".//ti:label", namespaces=NS)
        label_str = re.sub("\s+", " ", tostring(label[0], encoding=str)).replace("\n", "")
        self.assertIn(
            '<groupname xml:lang="eng">Martial</groupname>',
            label_str,
            "groupname should be exported correctly"
        )
        self.assertIn(
            '<title xml:lang="eng">Epigrammata</title>',
            label_str,
            "title should be exported correctly"
        )
        self.assertIn(
            '<description xml:lang="eng"> M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus </description>',
            label_str,
            "description should be exported correctly"
        )
        self.assertIn(
            '<label xml:lang="eng">Epigrammata</label>',
            label_str,
            "label should be exported correctly"
        )
        citation = Citation.ingest(label[0])
        self.assertEqual(
            len(citation), 3, "There should be three level of citation"
        )
        self.assertEqual(
            citation.name, "book", "First level is book"
        )
        if self.cache is not None:
            self.assertGreater(
                len(self.cache.cache._cache), 0,
                "There should be something cached"
            )

    def test_missing_request(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = self.app.get("/cts").data.decode("utf-8").replace("\n", "")
        self.assertIn(
            "Request missing one or more required parameters", data, "Error message should be displayed"
        )
        self.assertIn(
            "MissingParameter", data, "Error name should be displayed"
        )

    def test_UnknownCollection_request(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = self.app.get("/cts?request=GetCapabilities&urn=urn:cts:latinLit:phi1295").data.decode()
        self.assertIn(
            "Resource requested is not found", data, "Error message should be displayed"
        )
        self.assertIn(
            "UnknownCollection", data, "Error name should be displayed"
        )
        data = self.app.get("/cts?request=GetPassage&urn=urn:cts:latinLit:phi1294.phi003").data.decode()
        self.assertIn(
            "Resource requested is not found", data, "Error message should be displayed"
        )
        self.assertIn(
            "UnknownCollection", data, "Error name should be displayed"
        )
        self.assertLogged("CTS error thrown UnknownCollection for request=GetCapabilities&urn=urn:cts:latinLit:phi1295 "
                          "( Resource requested is not found )")

    def test_InvalidUrn_request(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = self.app.get("/cts?request=GetPassage&urn=urn:cts:latinLit:phi1295").data.decode()
        self.assertIn(
            "Syntactically valid URN refers in invalid value ", data, "Error message should be displayed"
        )
        self.assertIn(
            "InvalidURN", data, "Error name should be displayed"
        )
        data = self.app.get("/cts?request=GetPassagePlus&urn=urn:cts:latinLit:phi1294").data.decode()
        self.assertIn(
            "Syntactically valid URN refers in invalid value ", data, "Error message should be displayed"
        )
        self.assertIn(
            "InvalidURN", data, "Error name should be displayed"
        )

    def test_get_firstUrn(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = self.app.get("/cts?request=GetFirstUrn&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2:1").data.decode()
        self.assertIn(
            "<urn>urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr</urn>", data, "First URN is displayed"
        )
        self.assertEqual(
            (data.startswith("<GetFirstUrn"), data.endswith("</GetFirstUrn>")), (True, True), "Nodes are Correct"
        )

    def test_dts_collection_route(self):
        """ Check that DTS Main collection works """
        response = self.app.get("/dts/collections")
        data = json.loads(response.data.decode())
        compared_to = self.resolver.getMetadata().export(Mimetypes.JSON.DTS.Std)
        self.maxDiff = None
        self.assertCountEqual(
            data, compared_to, "Main Collection should export as JSON DTS STD"
        )
        self.assertEqual(
            response.status_code, 200, "Answer code should be correct"
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "*"
        )

    def test_dts_collection_target_route(self):
        """ Check that DTS Main collection works """
        response = self.app.get("/dts/collections/urn:cts:latinLit:phi1294")
        data = json.loads(response.data.decode())
        compared_to = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294").export(Mimetypes.JSON.DTS.Std)
        self.maxDiff = None
        self.assertCountEqual(
            data, compared_to, "Main Collection should export as JSON DTS STD"
        )
        self.assertEqual(
            response.status_code, 200, "Answer code should be correct"
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "*"
        )
        self.assertEqual(
            "urn:cts:latinLit:phi1294", data["@graph"]["@id"], "Label should be there"
        )

    def test_dts_UnknownCollection_request(self):
        """Check get Label"""
        # Need to parse with Citation and parse individually or simply check for some equality
        data = json.loads(self.app.get("/dts/collections/urn:cts:latinLit:phi1295").data.decode())
        self.assertIn(
            "Resource requested is not found", data["message"], "Error message should be displayed"
        )
        self.assertIn(
            "UnknownCollection", data["error"], "Error name should be displayed"
        )
        data = json.loads(self.app.get("/dts/collections/urn:cts:latinLit:phi1294.phi003").data.decode())
        self.assertIn(
            "Resource requested is not found", data["message"], "Error message should be displayed"
        )
        self.assertIn(
            "UnknownCollection", data["error"], "Error name should be displayed"
        )
        self.assertLogged("DTS error thrown UnknownCollection for /dts/collections/urn:cts:latinLit:phi1295 "
                          "( Resource requested is not found )")


class TestRestAPICache(TestRestAPI):
    def setUp(self):
        nautilus_cache = RedisCache()
        app = Flask("Nautilus")
        self.cache = Cache(config={'CACHE_TYPE': 'simple'})
        nautilus = FlaskNautilus(
            app=app,
            resolver=NautilusCTSResolver(["./tests/test_data/latinLit"]),
            flask_caching=self.cache
        )
        app.debug = True
        self.cache.init_app(app)
        self.app = app.test_client()
        self.parent = CTS("/cts")
        self.resolver = HttpCTSResolver(endpoint=self.parent)
        logassert.setup(self, nautilus.logger.name)

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

            request = self.app.get("/cts?{}".format(
                "&".join(
                    ["{}={}".format(key, value) for key, value in parameters.items()])
                )
            )
            self.parent.called.append(parameters)
            return request.data.decode()

        self.parent.called = []
        self.parent.call = lambda x: call(self.parent, x)
