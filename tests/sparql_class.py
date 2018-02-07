from MyCapytain.common.constants import set_graph, gen_graph
from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from .cts.config import sqlite_address
from unittest import TestCase


class Sparql(TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            SparqlAlchemyNautilusCTSResolver.clear_graph(sqlite_address)
        finally:
            set_graph(gen_graph())
