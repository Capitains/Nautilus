from tests.test_flask_ext.base import SetupModule, CTSModule, DTSModule, LoggingModule, logger
from capitains_nautilus.cts.resolver.base import NautilusCtsResolver
from unittest import TestCase
from MyCapytain.common.constants import set_graph, bind_graph, get_graph
from flask import Flask
from flask_caching import Cache
from capitains_nautilus.flask_ext import FlaskNautilus
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever
from logassert import logassert


class NautilusCTSResolverGenerator:
    ATTRIB_RESOLVER = True

    def generate_resolver(self, directories):
        if type(self).ATTRIB_RESOLVER:
            # If it was never run on current object
            if not hasattr(self, "__dirs__"):
                self.__dirs__ = []
                self.__resolver__ = None

            # If we changed the directories to parse
            if self.__dirs__ != directories:
                self.__resolver__ = None
                self.clear()

            # If we did not already create the resolver
            if not self.__resolver__:
                set_graph(bind_graph())
                self.__resolver__ = NautilusCtsResolver(directories)
                self.__resolver__.parse()

            return self.__resolver__

        set_graph(bind_graph())
        return NautilusCtsResolver(directories)

    def clear(self):
        g = get_graph()
        del g


class TestClassicCTSResolverRestAPI(NautilusCTSResolverGenerator, CTSModule, DTSModule, SetupModule, TestCase):
    """ Test the rest API with the legacy resolver that uses full file """


class TestClassicCTSResolverRestAPICache(CTSModule, DTSModule, TestCase, NautilusCTSResolverGenerator):
    """ Test the rest API cache handling with the legacy resolver that uses full file """
    ATTRIB_RESOLVER = False

    def setUp(self):
        self._app = Flask("Nautilus")
        self.cache = Cache(config={'CACHE_TYPE': 'simple'})
        self.nautilus = FlaskNautilus(
            app=self._app,
            resolver=NautilusCtsResolver(["./tests/test_data/latinLit"]),
            flask_caching=self.cache,
            logger=logger
        )
        self._app.debug = True
        self.cache.init_app(self._app)
        self.app = self._app.test_client()
        self.parent = HttpCtsRetriever("/cts")
        self.resolver = HttpCtsResolver(endpoint=self.parent)
        logassert.setup(self, self.nautilus.logger.name)
        self.nautilus.logger.disabled = True

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

    def tearDown(self):
        del self._app
        del self.app
        del self.nautilus

class TestClassicCTSResolverRestAPILogging(NautilusCTSResolverGenerator, LoggingModule, SetupModule, TestCase):
    """ Test the rest API logging system with the legacy resolver that uses full file """
