from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.constants import RDF_NAMESPACES


def NoneGenerator(object_id):
    return None


class SparqlNavigatedCollection(Collection):

    @staticmethod
    def children_class(object_id):
        return SparqlNavigatedCollection

    @staticmethod
    def parent_class(object_id):
        return SparqlNavigatedCollection

    @property
    def members(self):
        """ Children of the collection's item

        :rtype: [Collection]
        """
        return list(
            [
                self.children_class(self.graph.objects(self.asNode(), RDF_NAMESPACES.DTS.parent))
            ]
        )

    @property
    def parent(self):
        """ Parent of current object

        :rtype: Collection
        """
        parent = self.graph.objects(self.asNode(), RDF_NAMESPACES.DTS.parent)
        if parent:
            return self.parent_class(parent[0])
        return None

    @property
    def children(self):
        return {
            collection.id: collection for collection in self.members
        }
