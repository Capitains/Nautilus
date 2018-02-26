from tests.test_flask_ext.base import SetupModule, CacheModule, CTSModule, DTSModule, LoggingModule
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from unittest import TestCase
from MyCapytain.common.constants import set_graph, bind_graph, get_graph


class NautilusCTSResolverGenerator:
    ATTRIB_RESOLVER = True

    def generate_resolver(self, directories):
        if type(self).ATTRIB_RESOLVER:
            if not hasattr(self, "__dirs__"):
                self.__dirs__ = []
                self.__resolver__ = None
            if self.__dirs__ != directories:
                self.__resolver__ = None
                self.clear()
            if not self.__resolver__:
                set_graph(bind_graph())
                self.__resolver__ = NautilusCTSResolver(directories)
            return self.__resolver__
        set_graph(bind_graph())
        x = NautilusCTSResolver(directories)
        x.parse()
        return x

    def clear(self):
        g = get_graph()
        del g


class TestClassicCTSResolverRestAPI(NautilusCTSResolverGenerator, CTSModule, DTSModule, SetupModule, TestCase):
    """ Test the rest API with the legacy resolver that uses full file """


class TestClassicCTSResolverRestAPICache(NautilusCTSResolverGenerator, CTSModule, DTSModule, CacheModule, TestCase):
    """ Test the rest API cache handling with the legacy resolver that uses full file """
    ATTRIB_RESOLVER = False


class TestClassicCTSResolverRestAPILogging(NautilusCTSResolverGenerator, LoggingModule, SetupModule, TestCase):
    """ Test the rest API logging system with the legacy resolver that uses full file """
