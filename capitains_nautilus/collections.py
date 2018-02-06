from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.constants import RDF_NAMESPACES, get_graph
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.reference import URN
from rdflib import URIRef, RDF


def NoneGenerator(object_id):
    return None


class SparqlNavigatedCollection(Collection):
    def __init__(self, *args, **kwargs):
        identifier = None
        if len(args) > 0:
            identifier = args[0]
        elif len(kwargs) > 0:
            if "identifier" in kwargs:
                identifier = kwargs["identifier"]
            elif "urn" in kwargs:
                identifier = kwargs["urn"]

        if self.exists(identifier):
            self._simple_init(identifier)
        else:
            super(SparqlNavigatedCollection, self).__init__(*args, **kwargs)

    def exists(self, identifier):
        if not identifier:
            return False
        query = list(self.graph.objects(identifier, RDF.type))
        return len(query) > 0

    def _simple_init(self, identifier):
        self.__node__ = URIRef(identifier)
        self.__metadata__ = Metadata(node=self.asNode())
        self.__capabilities__ = Metadata.getOr(self.asNode(), RDF_NAMESPACES.DTS.capabilities)

    @property
    def graph(self):
        return get_graph()

    @staticmethod
    def children_class(object_id):
        return SparqlNavigatedCollection(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlNavigatedCollection(object_id)

    @property
    def members(self):
        """ Children of the collection's item

        :rtype: [Collection]
        """
        return list(
            [
                self.children_class(child)
                for child in self.graph.subjects(RDF_NAMESPACES.DTS.parent, self.asNode())
            ]
        )

    @property
    def parent(self):
        """ Parent of current object

        :rtype: Collection
        """
        parent = list(self.graph.objects(self.asNode(), RDF_NAMESPACES.DTS.parent))
        if parent:
            return self.parent_class(parent[0])
        return None

    @parent.setter
    def parent(self, parent):
        self.graph.set(
            (self.asNode(), RDF_NAMESPACES.DTS.parent, parent.asNode())
        )

    @property
    def children(self):
        return {
            collection.id: collection for collection in self.members
        }


class CTSSparqlNavigatedCollection(SparqlNavigatedCollection):
    def _simple_init(self, identifier):
        if isinstance(identifier, URN):
            self.__urn__ = identifier
        else:
            self.__urn__ = URN(str(identifier))
        super(CTSSparqlNavigatedCollection, self)._simple_init(identifier)
