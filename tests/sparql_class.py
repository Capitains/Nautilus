from capitains_nautilus.collections.sparql import clear_graph
from .cts.config import sqlite_address
from unittest import TestCase


class Sparql(TestCase):
    @classmethod
    def setUpClass(cls):
        print("Clearing")
        try:
            clear_graph(sqlite_address)
        except Exception as E:
            print("Failed clearing", E)
            pass

    def tearDown(self):
        clear_graph(sqlite_address)
