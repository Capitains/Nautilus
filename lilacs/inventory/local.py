from MyCapytain.resources.inventory import TextInventory, TextGroup, Work
from MyCapytain.common.reference import URN
from glob import glob
import os.path
from lilacs.inventory.proto import InventoryResolver


class XMLFolderResolver(InventoryResolver):
    """ XML Folder Based resolver.

     .. warning :: This resolver does not support inventories
     """
    def __init__(self, resource, cache_folder="./cache"):
        """ Initiate the XMLResolver

        :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
        :type resource: [str]
        """
        super(XMLFolderResolver, self).__init__(resource=TextInventory())

        self.works = []
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                with open(__cts__) as __xml__:
                    textgroup = TextGroup(resource=__xml__)
                    textgroup.urn = URN(textgroup.xml.get("urn"))
                self.resource.textgroups[str(textgroup.urn)] = textgroup

                for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                    with open(__subcts__) as __xml__:
                        work = Work(resource=__xml__)
                        work.urn = URN(work.xml.get("urn"))
                    self.resource.textgroups[str(textgroup.urn)].works[str(work.urn)] = work