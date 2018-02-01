from .test_resolver import TestXMLFolderResolverBehindTheScene, TextXMLFolderResolver, TextXMLFolderResolverDispatcher
from capitains_nautilus.cts.resolver import SparqlNautilusCTSResolver

class _Parser:
    def RESOLVER_CLASS(self, *args, **kwargs):
        x = SparqlNautilusCTSResolver(*args, **kwargs)
        x.parse()
        print("I parsed !")
        return x

class TestSparqlBasedResolverDispatcher(_Parser, TextXMLFolderResolverDispatcher):
    """"""


class TextSparqlXMLFolderResolver(_Parser, TextXMLFolderResolver):
    """"""


class TestSparqlXMLFolderResolverBehindTheScene(_Parser, TestXMLFolderResolverBehindTheScene):
    """ """