from .test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlNautilusCTSResolver


class TestSparqlBasedResolverDispatcher(TextXMLFolderResolverDispatcher):
    RESOLVER_CLASS = SparqlNautilusCTSResolver


class TextSparqlXMLFolderResolver(TextXMLFolderResolver):
    RESOLVER_CLASS = SparqlNautilusCTSResolver


class TestSparqlXMLFolderResolverBehindTheScene(TestXMLFolderResolverBehindTheScene):
    RESOLVER_CLASS = SparqlNautilusCTSResolver