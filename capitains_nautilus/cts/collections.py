from MyCapytain.resources.collections.cts import (
    XmlCtsTextInventoryMetadata,
    XmlCtsTextgroupMetadata,
    XmlCtsWorkMetadata,
    XmlCtsCitation,
    XmlCtsEditionMetadata
)
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection
from capitains_nautilus.collections import SparqlNavigatedCollection


class SparqlXmlCitation(XmlCtsCitation):
    """ Need to keep citation information here in the Graph """
    pass


class SparqlXmlCtsEditionMetadata(SparqlNavigatedCollection, XmlCtsEditionMetadata):
    @staticmethod
    def children_class(object_id):
        return lambda *x: None

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsWorkMetadata


class SparqlXmlCtsWorkMetadata(SparqlNavigatedCollection, XmlCtsWorkMetadata):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsEditionMetadata

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextgroupMetadata


class SparqlXmlCtsTextgroupMetadata(SparqlNavigatedCollection, XmlCtsTextgroupMetadata):
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsWorkMetadata

    @staticmethod
    def parent_class(object_id):
        return SparqlXmlCtsTextInventoryMetadata


class SparqlXmlCtsTextInventoryMetadata(SparqlNavigatedCollection, XmlCtsTextInventoryMetadata):
    """ Collection that does tree traversal based on Sparql queries on the local Graph

    """
    @staticmethod
    def children_class(object_id):
        return SparqlXmlCtsTextgroupMetadata

    @staticmethod
    def parent_class(object_id):
        return CtsTextInventoryCollection