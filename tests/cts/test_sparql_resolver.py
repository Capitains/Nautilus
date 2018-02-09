from tests.cts.test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from .config import sqlite_address
from ..sparql_class import Sparql


class _Parser(Sparql):
    RESOLVER_CLASS = SparqlAlchemyNautilusCTSResolver


class TestSparqlBasedResolverDispatcher(_Parser, TextXMLFolderResolverDispatcher):
    """"""
    def generate_repository(self, resource, dispatcher=None, remove_empty=True):
        Repository = self.RESOLVER_CLASS(resource, dispatcher=dispatcher, sqlalchemy_address=sqlite_address)
        Repository.logger.disabled = True
        Repository.REMOVE_EMPTY = remove_empty

        Repository.parse()
        return Repository

    def setUp(self):
        Repository = self.RESOLVER_CLASS([], sqlalchemy_address=sqlite_address)
        Repository.clear()


class TextSparqlXMLFolderResolver(_Parser, TextXMLFolderResolver):
    """"""
    def setUp(self):
        self.resolver = self.RESOLVER_CLASS(["./tests/testing_data/latinLit2"], sqlalchemy_address=sqlite_address)
        self.resolver.parse()


class TestSparqlXMLFolderResolverBehindTheScene(_Parser, TestXMLFolderResolverBehindTheScene):
    """ """

    def generate_repository(self, *args, **kwargs):
        print("Generate")
        if "sqlalchemy_address" not in kwargs:
            kwargs["sqlalchemy_address"] = sqlite_address

        Repository = self.RESOLVER_CLASS(*args, **kwargs)

        Repository.parse()
        print("Parsed")
        return Repository

    def setUp(self):
        print("\nClearing")
        try:
            self.RESOLVER_CLASS.clear_graph(sqlite_address)
        except:
            pass

    def test_get_capabilities_nocites(self):
        """ Check Get Capabilities latinLit data"""
        Repository = self.generate_repository(
            ["./tests/testing_data/latinLit"]
        )
        print("Generated ?")
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit:stoa0045.stoa008.perseus-lat2")[0]), 0,
            "Texts without citations were ignored"
        )

    def test_get_shared_textgroup_cross_repo(self):
        """ Check Get Capabilities """
        Repository = self.generate_repository(
            [
                "./tests/testing_data/farsiLit",
                "./tests/testing_data/latinLit2"
            ]
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.perseus-lat2"),
            "We should find perseus-lat2"
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.opp-lat2"),
            "We should find perseus-lat2"
        )