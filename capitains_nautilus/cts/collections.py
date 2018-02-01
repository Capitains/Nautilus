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
from MyCapytain.common.constants import RDF_NAMESPACES
from capitains_nautilus.collections import SparqlNavigatedCollection


class SparqlXmlCtsTextMetadata(SparqlNavigatedCollection, XmlCtsTextMetadata):
    @staticmethod
    def children_class(object_id):
        raise NameError("CTS Text cannot have children")

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsWorkMetadata(urn=object_id)

    @property
    def readable(self):
        return True

    @property
    def path(self):
        print("Called")
        return list(self.graph.objects(self.asNode(), RDF_NAMESPACES.CAPITAINS.path))[0]

    @path.setter
    def path(self, value):
        print("Setting the path ?")
        self.graph.set(
            (self.asNode(), RDF_NAMESPACES.CAPITAINS.path, value)
        )


class SparqlXmlCitation(XmlCtsCitation):
    """ Need to keep citation information here in the Graph """
    pass


class SparqlXmlCtsTranslationMetadata(SparqlXmlCtsTextMetadata, XmlCtsTranslationMetadata):
    """ """


class SparqlXmlCtsCommentaryMetadata(SparqlXmlCtsTextMetadata, XmlCtsCommentaryMetadata):
    """ """


class SparqlXmlCtsEditionMetadata(SparqlXmlCtsTextMetadata, XmlCtsEditionMetadata):
    """ """


class SparqlXmlCtsWorkMetadata(SparqlNavigatedCollection, XmlCtsWorkMetadata):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsEditionMetadata(object_id)

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextgroupMetadata(object_id)


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
        return CtsTextInventoryCollection(object_id)
