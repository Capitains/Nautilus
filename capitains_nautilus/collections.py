from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.constants import RDF_NAMESPACES


def NoneGenerator(object_id):
    return None


class SparqlNavigatedCollection(Collection):

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
