from MyCapytain.common.reference import URN
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
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection, PrototypeCtsCollection
from MyCapytain.common.constants import RDF_NAMESPACES, get_graph
from capitains_nautilus.collections.sparql import SparqlNavigatedCollection
from rdflib import BNode, Literal, RDF, URIRef
from capitains_nautilus.errors import UnknownCollection
from capitains_nautilus.utils.performances import cached_property, STORE


class CTSSparqlNavigatedCollection(PrototypeCtsCollection, SparqlNavigatedCollection):
    def _simple_init(self, identifier):
        if isinstance(identifier, URN):
            self.__urn__ = identifier
        else:
            self.__urn__ = URN(str(identifier))
        super(CTSSparqlNavigatedCollection, self)._simple_init(identifier)

    def set_cts_property(self, prop, value, lang=None):
        if not isinstance(value, Literal):
            value = Literal(value, lang=lang)
        _prop = RDF_NAMESPACES.CTS.term(prop)

        if not (self.asNode(), _prop, value) in self.graph:
            super(CTSSparqlNavigatedCollection, self).set_cts_property(prop, value)


class SparqlXmlCtsTextMetadata(CTSSparqlNavigatedCollection, XmlCtsTextMetadata):
    @staticmethod
    def children_class(object_id):
        raise NameError("CTS Text cannot have children")

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsWorkMetadata(object_id)

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
    CLASS_EDITION = SparqlXmlCtsEditionMetadata
    CLASS_TRANSLATION = SparqlXmlCtsTranslationMetadata
    CLASS_COMMENTARY = SparqlXmlCtsCommentaryMetadata
    CLASS_CITATION = SparqlXmlCitation

    @classmethod
    def children_class(cls, object_id):
        o = list(get_graph().objects(object_id, RDF.type))[0]

        if o == SparqlXmlCtsEditionMetadata.TYPE_URI:
            return SparqlXmlCtsEditionMetadata(object_id)
        elif o == XmlCtsTranslationMetadata.TYPE_URI:
            return SparqlXmlCtsTranslationMetadata(object_id)
        elif o == XmlCtsCommentaryMetadata.TYPE_URI:
            return SparqlXmlCtsCommentaryMetadata(object_id)

    @classmethod
    def parent_class(cls, object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)

    @property
    def texts(self):
        return self.children

    def update(self, other):
        pass

    def decide_class(self, key):
        if key == self.id:
            return self
        o = self.get_type(key)
        if o:
            if o == SparqlXmlCtsEditionMetadata.TYPE_URI:
                return SparqlXmlCtsEditionMetadata(key)
            elif o == XmlCtsTranslationMetadata.TYPE_URI:
                return SparqlXmlCtsTranslationMetadata(key)
            elif o == XmlCtsCommentaryMetadata.TYPE_URI:
                return SparqlXmlCtsCommentaryMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlXmlCtsTextgroupMetadata(CTSSparqlNavigatedCollection, XmlCtsTextgroupMetadata):
    CLASS_WORK = SparqlXmlCtsWorkMetadata

    @classmethod
    def children_class(cls, object_id):
        return cls.CLASS_WORK(object_id)

    @classmethod
    def parent_class(cls, object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)

    def update(self, other):
        pass

    def decide_class(self, key):
        if key == self.id:
            return self
        o = self.get_type(key)
        if o:
            if o == SparqlXmlCtsEditionMetadata.TYPE_URI:
                return SparqlXmlCtsEditionMetadata(key)
            elif o == XmlCtsTranslationMetadata.TYPE_URI:
                return SparqlXmlCtsTranslationMetadata(key)
            elif o == XmlCtsCommentaryMetadata.TYPE_URI:
                return SparqlXmlCtsCommentaryMetadata(key)
            elif o == SparqlXmlCtsWorkMetadata.TYPE_URI:
                return SparqlXmlCtsWorkMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlXmlCtsTextInventoryMetadata(SparqlNavigatedCollection, XmlCtsTextInventoryMetadata):
    """ Collection that does tree traversal based on Sparql queries on the local Graph

    """
    CLASS_TEXTGROUP = SparqlXmlCtsTextgroupMetadata

    @classmethod
    def children_class(cls, object_id):
        return cls.CLASS_TEXTGROUP(object_id)

    @classmethod
    def parent_class(cls, object_id):
        return SparqlTextInventoryCollection(object_id)

    def decide_class(self, key):
        if key == self.id:
            return self
        o = self.get_type(key)
        if o:
            if o == SparqlXmlCtsEditionMetadata.TYPE_URI:
                return SparqlXmlCtsEditionMetadata(key)
            elif o == XmlCtsTranslationMetadata.TYPE_URI:
                return SparqlXmlCtsTranslationMetadata(key)
            elif o == XmlCtsCommentaryMetadata.TYPE_URI:
                return SparqlXmlCtsCommentaryMetadata(key)
            elif o == SparqlXmlCtsWorkMetadata.TYPE_URI:
                return SparqlXmlCtsWorkMetadata(key)
            elif o == SparqlXmlCtsTextgroupMetadata.TYPE_URI:
                return SparqlXmlCtsTextgroupMetadata(key)
        raise UnknownCollection("%s is not part of this object" % key)


class SparqlTextInventoryCollection(SparqlNavigatedCollection, CtsTextInventoryCollection):
    def __init__(self, identifier="default"):
        super(SparqlTextInventoryCollection, self).__init__(identifier)

    @classmethod
    def children_class(cls, object_id):
        return SparqlXmlCtsTextInventoryMetadata(object_id)

    @classmethod
    def parent_class(cls, object_id):
        raise NameError("Text Inventory Collection cannot have parents")

    def decide_class(self, key):
        if key == self.id:
            return self
        o = self.get_type(key)
        if o:
            if o == SparqlXmlCtsEditionMetadata.TYPE_URI:
                return SparqlXmlCtsEditionMetadata(key)
            elif o == XmlCtsTranslationMetadata.TYPE_URI:
                return SparqlXmlCtsTranslationMetadata(key)
            elif o == XmlCtsCommentaryMetadata.TYPE_URI:
                return SparqlXmlCtsCommentaryMetadata(key)
            elif o == SparqlXmlCtsWorkMetadata.TYPE_URI:
                return SparqlXmlCtsWorkMetadata(key)
            elif o == SparqlXmlCtsTextgroupMetadata.TYPE_URI:
                return SparqlXmlCtsTextgroupMetadata(key)
            elif o == SparqlXmlCtsTextInventoryMetadata.TYPE_URI:
                return SparqlXmlCtsTextInventoryMetadata(key)
        raise UnknownCollection("%s is not part of this object %s" % (key, self))

