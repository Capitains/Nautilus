from tests.cts.test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from .config import sqlite_address


class _Parser:
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

    def tearDown(self):
        self.resolver.clear()


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