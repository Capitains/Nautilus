from tests.cts.test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlNautilusCTSResolver


class _Parser:
    RESOLVER_CLASS = SparqlNautilusCTSResolver


class TestSparqlBasedResolverDispatcher(_Parser, TextXMLFolderResolverDispatcher):
    """"""


class TextSparqlXMLFolderResolver(_Parser, TextXMLFolderResolver):
    """"""


class TestSparqlXMLFolderResolverBehindTheScene(_Parser, TestXMLFolderResolverBehindTheScene):
    """ """