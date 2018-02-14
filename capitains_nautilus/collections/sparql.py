from MyCapytain.common.constants import RDF_NAMESPACES, get_graph, set_graph, GRAPH_BINDINGS
from MyCapytain.common.metadata import Metadata
from MyCapytain.resources.prototypes.metadata import Collection
from rdflib import Literal, RDFS, RDF, URIRef, Graph, plugin
from rdflib.store import Store
from rdflib_sqlalchemy import registerplugins
from rdflib.namespace import SKOS
from capitains_nautilus.errors import UnknownCollection
from warnings import warn


def clear_graph(identifier=None):
    """ Clean up a graph by removing it

    :param identifier: Root identifier of the graph
    :return:
    """
    graph = get_graph()
    if identifier:
        graph.destroy(identifier)
    try:
        graph.close()
    except:
        warn("Unable to close the Graph")


def generate_alchemy_graph(alchemy_uri, prefixes=None, identifier="NautilusSparql"):
    """ Generate a graph and change the global graph to this one

    :param alchemy_uri: A Uri for the graph
    :param prefixes: A dictionary of prefixes and namespaces to bind to the graph
    :param identifier: An identifier that will identify the Graph root
    """
    registerplugins()
    ident = URIRef(identifier)
    uri = Literal(alchemy_uri)
    store = plugin.get("SQLAlchemy", Store)(identifier=ident)
    graph = Graph(store, identifier=ident)
    graph.open(uri, create=True)

    for prefix, ns in (prefixes or GRAPH_BINDINGS).items():
        if prefix == "":
            prefix = "cts"  # Fix until ALchemy Store accepts empty prefixes
        graph.bind(prefix, ns)

    return graph, identifier, uri


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
            elif "name" in kwargs:
                identifier = kwargs["name"]

        if self.exists(identifier):
            self._simple_init(identifier)
        else:
            super(SparqlNavigatedCollection, self).__init__(*args, **kwargs)

    def set_label(self, label, lang):
        """ Add the label of the collection in given lang

        :param label: Label Value
        :param lang:  Language code
        """
        try:
            self.metadata.add(SKOS.prefLabel, Literal(label, lang=lang))
            self.graph.addN([
                (self.asNode(), RDFS.label, Literal(label, lang=lang), self.graph),
            ])
        except Exception as E:
            print("Already tried ?", E)

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

    def decide_class(self, key):
        return type(self)(key)

    def __getitem__(self, item):
        if item in self:
            return self.decide_class(item)
        raise UnknownCollection("%s does not contain %s" % (self, item))

    @property
    def descendants(self):
        return list(
            [
                self.decide_class(child)
                for child, *_ in self.graph.query(
                    """
                    select ?desc
                    where {
                      ?desc <"""+RDF_NAMESPACES.DTS.parent+""">+ <"""+self.id+"""> .
                    }"""
                )
            ]
        )

    def get_type(self, key):
        query_key = key
        if isinstance(query_key, str):
            query_key = URIRef(query_key)
        for x in self.graph.objects(query_key, RDF.type):
            return x

    def __contains__(self, item):
        return bool(list(self.graph.query(
                """
                SELECT ?type
                where {
                  <""" + item + """> <""" + RDF_NAMESPACES.DTS.parent + """>+ <""" + self.id + """> .
                  <""" + item + """> a ?type
                }
                LIMIT 1
                """
            )
        ))

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
        print(self, "parent", parent)
        self.graph.set(
            (self.asNode(), RDF_NAMESPACES.DTS.parent, parent.asNode())
        )

    @property
    def children(self):
        return {
            collection.id: collection for collection in self.members
        }


