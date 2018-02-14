from tests.cts.test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from capitains_nautilus.collections.sparql import generate_alchemy_graph, clear_graph
from MyCapytain.common.constants import set_graph
from .config import sqlite_address
from ..sparql_class import Sparql


class _Parser(Sparql):
    RESOLVER_CLASS = SparqlAlchemyNautilusCTSResolver


class TestSparqlBasedResolverDispatcher(_Parser, TextXMLFolderResolverDispatcher):
    """"""
    def generate_repository(self, resource, dispatcher=None, remove_empty=True):
        if self.generated_graphs >= 1:
            clear_graph(self.graph_identifier)
            self.gen_graph()
        repo = self.RESOLVER_CLASS(resource, dispatcher=dispatcher, graph=self.graph)
        repo.logger.disabled = True
        repo.REMOVE_EMPTY = remove_empty
        repo.parse()
        self.generated_graphs += 1
        return repo

    def gen_graph(self):
        self.graph, self.graph_identifier, self.store_uri = generate_alchemy_graph(alchemy_uri=sqlite_address)
        set_graph(self.graph)

    def setUp(self):
        self.generated_graphs = 0
        self.gen_graph()

    def tearDown(self):
        clear_graph(self.graph_identifier)


class TextSparqlXMLFolderResolver(_Parser, TextXMLFolderResolver):
    """"""
    def setUp(self):
        self.graph, self.graph_identifier, self.store_uri = generate_alchemy_graph(alchemy_uri=sqlite_address)
        self.resolver = self.RESOLVER_CLASS(["./tests/testing_data/latinLit2"], graph=self.graph)
        self.resolver.parse()

    def tearDown(self):
        clear_graph(self.graph_identifier)


class TestSparqlXMLFolderResolverBehindTheScene(_Parser, TestXMLFolderResolverBehindTheScene):
    """ """

    def generate_repository(self, *args, **kwargs):
        if "graph" not in kwargs:
            kwargs["graph"] = self.graph

        print(kwargs)
        repository = self.RESOLVER_CLASS(*args, **kwargs)

        repository.parse()
        return repository

    def setUp(self):
        self.graph, self.graph_identifier, self.store_uri = generate_alchemy_graph(alchemy_uri=sqlite_address)
        set_graph(self.graph)

    def tearDown(self):
        clear_graph(self.graph)

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