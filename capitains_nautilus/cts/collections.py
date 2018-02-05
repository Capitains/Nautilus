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
from capitains_nautilus.collections import SparqlNavigatedCollection
from rdflib import BNode, Literal, RDF


class SparqlXmlCtsTextMetadata(SparqlNavigatedCollection, XmlCtsTextMetadata):
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
        super(SparqlXmlCitation, self).__upRefsDecl()
        print("I am updating !")
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


class SparqlXmlCtsTranslationMetadata(SparqlXmlCtsTextMetadata, XmlCtsTranslationMetadata):
    TYPE_URI = XmlCtsTranslationMetadata.TYPE_URI
    """ """


class SparqlXmlCtsCommentaryMetadata(SparqlXmlCtsTextMetadata, XmlCtsCommentaryMetadata):
    TYPE_URI = XmlCtsCommentaryMetadata.TYPE_URI
    """ """


class SparqlXmlCtsEditionMetadata(SparqlXmlCtsTextMetadata, XmlCtsEditionMetadata):
    TYPE_URI = XmlCtsEditionMetadata.TYPE_URI
    """ """


class SparqlXmlCtsWorkMetadata(SparqlNavigatedCollection, XmlCtsWorkMetadata):
    @staticmethod
    def children_class(object_id):
        o = list(get_graph().objects(object_id, RDF.type))[0]
        _type = o.split("/")[-1]

        if _type == "edition":
            return SparqlXmlCtsEditionMetadata.from_id(object_id)
        elif _type == "translation":
            return SparqlXmlCtsTranslationMetadata.from_id(object_id)
        elif _type == "commentary":
            return SparqlXmlCtsCommentaryMetadata.from_id(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)

    @property
    def texts(self):
        return self.children


class SparqlXmlCtsTextgroupMetadata(SparqlNavigatedCollection, XmlCtsTextgroupMetadata):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsWorkMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)


class SparqlXmlCtsTextInventoryMetadata(SparqlNavigatedCollection, XmlCtsTextInventoryMetadata):
    """ Collection that does tree traversal based on Sparql queries on the local Graph

    """

    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlTextInventoryCollection(object_id)


class SparqlTextInventoryCollection(SparqlNavigatedCollection, CtsTextInventoryCollection):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        raise NameError("Text Inventory Collection cannot have parents")