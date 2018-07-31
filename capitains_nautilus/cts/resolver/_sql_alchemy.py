from MyCapytain.resolvers.utils import CollectionDispatcher
from rdflib import Graph

from capitains_nautilus.collections.sparql import generate_alchemy_graph
from capitains_nautilus.cts.resolver.base import _SparqlSharedResolver


class SparqlAlchemyNautilusCtsResolver(_SparqlSharedResolver):
    def __init__(self, resource, name=None, logger=None, cache=None, dispatcher=None, graph=None, _workers=None):
        exceptions = []

        if graph is not None:
            if isinstance(graph, str):  # Graph is a string : is a SQLAlchemy identifier
                self.graph, self.graph_identifier, _ = generate_alchemy_graph(graph)
            elif isinstance(graph, Graph):
                self.graph = graph
                self.graph_identifier = graph.identifier
        else:
            self.graph, self.graph_identifier, _ = generate_alchemy_graph(graph)

        self._workers = _workers or 1

        if not dispatcher:
            # Normal init is setting label automatically
            inventory_collection = type(self).CLASSES["inventory_collection"](identifier="defaultTic")
            default_tiname = "/default"
            ti = type(self).CLASSES["inventory"](default_tiname)
            ti.parent = inventory_collection
            if ti.get_label(lang="eng") is None:
                ti.set_label("Default collection", "eng")
            dispatcher = CollectionDispatcher(inventory_collection,
                                              default_inventory_name=default_tiname)

        super(SparqlAlchemyNautilusCtsResolver, self).__init__(
            resource=resource,
            name=name,
            logger=logger,
            cache=cache,
            dispatcher=dispatcher
        )

        for exception in exceptions:
            self.logger.warning(exception)