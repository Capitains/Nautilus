from MyCapytain.resources.collections.cts import (
    XmlCtsTextInventoryMetadata,
    XmlCtsTextgroupMetadata,
    XmlCtsWorkMetadata,
    XmlCtsCitation,
    XmlCtsEditionMetadata,
    XmlCtsCommentaryMetadata,
    XmlCtsTranslationMetadata,
    XmlCtsTextMetadata
)
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection
from MyCapytain.common.constants import RDF_NAMESPACES, get_graph
from capitains_nautilus.collections import CTSSparqlNavigatedCollection, SparqlNavigatedCollection
from rdflib import BNode, Literal, RDF
from capitains_nautilus.errors import UnknownCollection


class SparqlXmlCtsTextMetadata(CTSSparqlNavigatedCollection, XmlCtsTextMetadata):
    @staticmethod
    def children_class(object_id):
        raise NameError("CTS Text cannot have children")

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsWorkMetadata(identifier=object_id)

    @property
    def readable(self):
        return True

    @property
    def path(self):
        for path in self.graph.objects(self.asNode(), RDF_NAMESPACES.CAPITAINS.path):
            return path

    @path.setter
    def path(self, value):
        if not self.path:
            self.graph.set(
                (self.asNode(), RDF_NAMESPACES.CAPITAINS.path, Literal(value))
            )

    @property
    def citation(self):
        for child in self.graph.objects(self.asNode(), RDF_NAMESPACES.CTS.citation):
            return SparqlXmlCitation(_bnode_id=child)

    @citation.setter
    def citation(self, value):
        if value:
            self.graph.set(
                (self.asNode(), RDF_NAMESPACES.CTS.citation, value.asNode())
            )

    @property
    def subtype(self):
        for _type in self.graph.objects(self.asNode(), RDF.type):
            x = str(_type).split("/")[-1].lower()
            print(self, x)
        return x


class SparqlXmlCitation(XmlCtsCitation):
    """ Need to keep citation information here in the Graph """

    def __init__(self, name=None, xpath=None, scope=None, refsDecl=None, child=None, _bnode_id=None):
        self.__graph__ = get_graph()
        self.__node__ = BNode(_bnode_id)
        super(SparqlXmlCitation, self).__init__(name=name, xpath=xpath, scope=scope, refsDecl=refsDecl, child=child)

    @property
    def graph(self):
        return self.__graph__

    def asNode(self):
        return self.__node__

    @property
    def child(self):
        for child in self.graph.objects(self.asNode(), RDF_NAMESPACES.CTS.citation):
            return SparqlXmlCitation(_bnode_id=child)

    @child.setter
    def child(self, value):
        self.graph.set(
            (self.asNode(), RDF_NAMESPACES.CTS.citation, value.asNode())
        )

    @property
    def refsDecl(self):
        """ ResfDecl expression of the citation scheme

        :rtype: str
        :Example: /tei:TEI/tei:text/tei:body/tei:div//tei:l[@n='$1']
        """
        for refsDecl in self.graph.objects(self.asNode(), RDF_NAMESPACES.TEI.replacementPattern):
            return str(refsDecl)

    def __upRefsDecl(self):
        self.graph.set(
            (self.asNode(), RDF_NAMESPACES.TEI.replacementPattern, Literal(self.__refsDecl))
        )

    @refsDecl.setter
    def refsDecl(self, val):
        XmlCtsCitation.refsDecl.fset(self, val)
        if val is not None:
            self.graph.set(
                (self.asNode(), RDF_NAMESPACES.TEI.replacementPattern, Literal(val))
            )

    @property
    def name(self):
        for refsDecl in self.graph.objects(self.asNode(), RDF_NAMESPACES.TEI.name):
            return str(refsDecl)

    @name.setter
    def name(self, val):
        XmlCtsCitation.name.fset(self, val)
        if val is not None:
            self.graph.set(
                (self.asNode(), RDF_NAMESPACES.TEI.name, Literal(val))
            )

    @property
    def members(self):
        return {}

    @property
    def descendants(self):
        return []

    @property
    def readableDescendants(self):
        return []


class SparqlXmlCtsTranslationMetadata(SparqlXmlCtsTextMetadata, XmlCtsTranslationMetadata):
    TYPE_URI = XmlCtsTranslationMetadata.TYPE_URI
    """ """


class SparqlXmlCtsCommentaryMetadata(SparqlXmlCtsTextMetadata, XmlCtsCommentaryMetadata):
    TYPE_URI = XmlCtsCommentaryMetadata.TYPE_URI
    """ """


class SparqlXmlCtsEditionMetadata(SparqlXmlCtsTextMetadata, XmlCtsEditionMetadata):
    TYPE_URI = XmlCtsEditionMetadata.TYPE_URI
    """ """


class SparqlXmlCtsWorkMetadata(CTSSparqlNavigatedCollection, XmlCtsWorkMetadata):
    @staticmethod
    def children_class(object_id):
        o = list(get_graph().objects(object_id, RDF.type))[0]
        _type = o.split("/")[-1]

        if _type == "edition":
            return SparqlXmlCtsEditionMetadata(object_id)
        elif _type == "translation":
            return SparqlXmlCtsTranslationMetadata(object_id)
        elif _type == "commentary":
            return SparqlXmlCtsCommentaryMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)

    @property
    def texts(self):
        return self.children

    def update(self, other):
        pass

    def __getitem__(self, key):
        return self.decide_class(key)

    def decide_class(self, key):
        o = list(get_graph().objects(key, RDF.type))
        if key == self.id:
            return self
        if len(o):
            _type = o[0].split("/")[-1]
            if _type == "edition":
                return SparqlXmlCtsEditionMetadata(key)
            elif _type == "translation":
                return SparqlXmlCtsTranslationMetadata(key)
            elif _type == "commentary":
                return SparqlXmlCtsCommentaryMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlXmlCtsTextgroupMetadata(CTSSparqlNavigatedCollection, XmlCtsTextgroupMetadata):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsWorkMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)

    def update(self, other):
        pass

    def __getitem__(self, key):
        return self.decide_class(key)

    def decide_class(self, key):
        o = list(get_graph().objects(key, RDF.type))
        if key == self.id:
            return self
        if len(o):
            _type = o[0].split("/")[-1]
            if _type == "edition":
                return SparqlXmlCtsEditionMetadata(key)
            elif _type == "translation":
                return SparqlXmlCtsTranslationMetadata(key)
            elif _type == "commentary":
                return SparqlXmlCtsCommentaryMetadata(key)
            elif _type == "work":
                return SparqlXmlCtsWorkMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlXmlCtsTextInventoryMetadata(SparqlNavigatedCollection, XmlCtsTextInventoryMetadata):
    """ Collection that does tree traversal based on Sparql queries on the local Graph

    """
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlTextInventoryCollection(object_id)

    def __getitem__(self, key):
        return self.decide_class(key)

    def decide_class(self, key):
        o = list(get_graph().objects(key, RDF.type))
        if len(o):
            _type = o[0].split("/")[-1]
            if _type == "edition":
                return SparqlXmlCtsEditionMetadata(key)
            elif _type == "translation":
                return SparqlXmlCtsTranslationMetadata(key)
            elif _type == "commentary":
                return SparqlXmlCtsCommentaryMetadata(key)
            elif _type == "work":
                return SparqlXmlCtsWorkMetadata(key)
            elif _type == "textgroup":
                return SparqlXmlCtsTextgroupMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlTextInventoryCollection(SparqlNavigatedCollection, CtsTextInventoryCollection):
    def __init__(self, identifier="default"):
        super(SparqlTextInventoryCollection, self).__init__(identifier)

    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        raise NameError("Text Inventory Collection cannot have parents")

    def __getitem__(self, key):
        return self.decide_class(key)

    def decide_class(self, key):
        o = list(get_graph().objects(key, RDF.type))
        if key == self.id:
            return self
        if len(o):
            _type = o[0].split("/")[-1]
            if _type == "edition":
                return SparqlXmlCtsEditionMetadata(key)
            elif _type == "translation":
                return SparqlXmlCtsTranslationMetadata(key)
            elif _type == "commentary":
                return SparqlXmlCtsCommentaryMetadata(key)
            elif _type == "work":
                return SparqlXmlCtsWorkMetadata(key)
            elif _type == "textgroup":
                return SparqlXmlCtsTextgroupMetadata(key)
            elif _type == "inventory":
                return SparqlXmlCtsTextInventoryMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)

