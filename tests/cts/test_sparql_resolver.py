from tests.cts.test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver


class _Parser:
    RESOLVER_CLASS = SparqlAlchemyNautilusCTSResolver


class TestSparqlBasedResolverDispatcher(_Parser, TextXMLFolderResolverDispatcher):
    """"""


class TextSparqlXMLFolderResolver(_Parser, TextXMLFolderResolver):
    """"""


class TestSparqlXMLFolderResolverBehindTheScene(_Parser, TestXMLFolderResolverBehindTheScene):
    """ """