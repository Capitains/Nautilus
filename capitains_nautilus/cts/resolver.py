from glob import glob
import os.path
import logging
from werkzeug.contrib.cache import NullCache

import MyCapytain.errors
from MyCapytain.common.reference import URN, Reference
from MyCapytain.resolvers.cts.local import CTSCapitainsLocalResolver
from MyCapytain.resolvers.utils import CollectionDispatcher
from MyCapytain.resources.collections.cts import TextInventory, TextGroup, Work, Citation, Edition
from MyCapytain.resources.prototypes.cts.inventory import TextInventoryCollection
from MyCapytain.resources.texts.locals.tei import Text

from capitains_nautilus import _cache_key
from capitains_nautilus.errors import *


class NautilusCTSResolver(CTSCapitainsLocalResolver):
    """ XML Folder Based resolver.

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]
    :param name: Key used to make cache key
    :param cache: Cache object to be used for the inventory
    :type cache: BaseCache
    :param logger: Logging object
    :type logger: logging

    :ivar inventory_cache_key: Werkzeug Cache key to get or set cache for the TextInventory
    :ivar texts_cache_key:  Werkzeug Cache key to get or set cache for lists of metadata texts objects
    :ivar texts_parsed:  Werkzeug Cache key to get or set cache for lists of parsed texts objects
    :ivar texts: List of Text Metadata objects
    :ivar source: Original resource parameter

    .. warning :: This resolver does not support inventories
    """
    TIMEOUT = None
    NautilusCTSResolver = False

    def __init__(self, resource, name=None, logger=None, cache=None, dispatcher=None):
        """ Initiate the XMLResolver

        """
        if dispatcher is None:
            inventory_collection = TextInventoryCollection(identifier="defaultTic")
            ti = TextInventory("default")
            ti.parent = inventory_collection
            ti.set_label("Default collection", "eng")
            self.dispatcher = CollectionDispatcher(inventory_collection)
        else:
            self.dispatcher = dispatcher

        self.__inventory__ = None
        self.__texts__ = []
        self.name = name

        self.logger = logger
        if not logger:
            self.logger = logging.getLogger(name)

        if not name:
            self.name = "repository"

        if cache is None:
            cache = NullCache()

        self.__cache__ = cache
        self.__resources__ = resource
        self.__parsed__ = False

        self.inventory_cache_key = _cache_key("Nautilus", self.name, "Inventory", "Resources")
        self.texts_metadata_cache_key = _cache_key("Nautilus", self.name, "Inventory", "TextsMetadata")
        self.texts_parsed_cache_key = _cache_key("Nautilus", self.name, "Inventory", "TextsParsed")

        # Parse if no Cache
        # self.get_or(self.inventory_cache_key, self.parse)

    @property
    def cache(self):
        return self.__cache__

    @property
    def inventory(self):
        if self.__parsed__ is False:
            self.__inventory__ = self.get_or(self.inventory_cache_key, self.parse, self.__resources__, ret="inventory")
        return self.__inventory__

    @inventory.setter
    def inventory(self, value):
        self.__inventory__ = value
        self.cache.set(self.inventory_cache_key, value)

    @property
    def texts(self):
        """ List of text known

        :rtype: list
        """
        if self.__texts__ is None:
            self.__texts__ = self.get_or(self.texts_metadata_cache_key, self.parse, self.__resources__, ret="texts")
        return self.__texts__

    @texts.setter
    def texts(self, value):
        self.__texts__ = value
        self.cache.set(self.texts_metadata_cache_key, value)

    def xmlparse(self, file):
        """ Parse a XML file

        :param file: Opened File
        :return: Tree
        """
        return self.get_or(
            _cache_key("Nautilus", self.name, "File", "Tree", file.name), CTSCapitainsLocalResolver.xmlparse, self, file
        )

    def get_or(self, cache_key, callback, *args, **kwargs):
        """ Get or set the cache using callback and arguments

        :param cache_key: Cache key for given resource
        :param callback: Callback if object does not exist
        :param args: Ordered Argument for the callback
        :param kwargs: Keyword argument for the callback
        :return: Output of the callback
        """
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        else:
            try:
                output = callback(*args, **kwargs)
            except MyCapytain.errors.UnknownCollection as E:
                raise UnknownCollection(str(E))
            except Exception as E:
                raise E
            self.cache.set(cache_key, output, self.TIMEOUT)
            return output

    def read(self, identifier, path=None):
        """ Read a text object given an identifier and a path

        :param identifier: Identifier of the text
        :param path: Path of the text files
        :return: Text
        """
        o = self.cache.get(_cache_key(self.texts_parsed_cache_key, identifier))
        if o is not None:
            return o
        else:
            with open(path) as f:
                o = Text(urn=identifier, resource=self.xmlparse(f))
                self.cache.set(_cache_key(self.texts_parsed_cache_key, identifier), o)
        return o

    def flush(self):
        """ Flush current resolver objects and cache
        """
        for text in self.texts:
            self.cache.delete(_cache_key(self.texts_parsed_cache_key, str(text.id)))
        self.cache.delete(self.inventory_cache_key)
        self.cache.delete(self.texts_metadata_cache_key)

    def parse(self, resource=None, ret="inventory"):
        """ Parse a list of directories ans
        :param resource: List of folders
        :param ret: Return a specific item ("inventory" or "texts")
        """
        if resource is None:
            resource = self.__resources__
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                try:
                    with open(__cts__) as __xml__:
                        textgroup = TextGroup.parse(
                            resource=__xml__
                        )
                        tg_urn = str(textgroup.urn)
                    if tg_urn in self.dispatcher.collection:
                        self.dispatcher.collection[tg_urn].update(textgroup)
                    else:
                        self.dispatcher.dispatch(textgroup, path=__cts__)

                    for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                        with open(__subcts__) as __xml__:
                            work = Work.parse(
                                resource=__xml__,
                                parent=self.dispatcher.collection[tg_urn]
                            )
                            work_urn = str(work.urn)
                            if work_urn in self.dispatcher.collection[tg_urn].works:
                                self.dispatcher.collection[work_urn].update(work)

                        for __textkey__ in work.texts:
                            __text__ = self.dispatcher.collection[__textkey__]
                            __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                                directory=os.path.dirname(__subcts__),
                                textgroup=__text__.urn.textgroup,
                                work=__text__.urn.work,
                                version=__text__.urn.version
                            )
                            if os.path.isfile(__text__.path):
                                try:
                                    t = self.read(__textkey__, __text__.path)
                                    cites = list()
                                    for cite in [c for c in t.citation][::-1]:
                                        if len(cites) >= 1:
                                            cites.append(Citation(
                                                xpath=cite.xpath.replace("'", '"'),
                                                scope=cite.scope.replace("'", '"'),
                                                name=cite.name,
                                                child=cites[-1]
                                            ))
                                        else:
                                            cites.append(Citation(
                                                xpath=cite.xpath.replace("'", '"'),
                                                scope=cite.scope.replace("'", '"'),
                                                name=cite.name
                                            ))
                                    del t
                                    __text__.citation = cites[-1]
                                    self.logger.info("%s has been parsed ", __text__.path)
                                    if __text__.citation.isEmpty() is False:
                                        self.texts.append(__text__)
                                    else:
                                        self.logger.error("%s has no passages", __text__.path)
                                except Exception as E:
                                    self.logger.error(
                                        "%s does not accept parsing at some level (most probably citation) ",
                                        __text__.path
                                    )
                            else:
                                self.logger.error("%s is not present", __text__.path)
                except MyCapytain.errors.UndispatchedTextError as E:
                    self.logger.error("Error dispatching %s ", __cts__)
                    if self.RAISE_ON_UNDISPATCHED is True:
                        raise UndispatchedTextError(E)
                except Exception as E:
                    print(E)
                    self.logger.error("Error parsing %s ", __cts__)

        self.inventory = self.dispatcher.collection
        self.texts = self.__texts__
        if ret == "texts":
            return self.__texts__
        else:
            return self.__inventory__

    def __getText__(self, urn):
        """ Returns a PrototypeText object
        :param urn: URN of a text to retrieve
        :type urn: str, URN
        :return: Textual resource and metadata
        :rtype: (Text, InventoryText)
        """
        if not isinstance(urn, URN):
            urn = URN(urn)
        if len(urn) != 5:
            if len(urn) == 4:
                urn, reference = urn.upTo(URN.WORK), str(urn.reference)
                urn = [
                    t.id
                    for t in self.__texts__
                    if t.id.startswith(str(urn)) and isinstance(t, Edition) and not print(t.id)
                ]
                if len(urn) > 0:
                    urn = URN(urn[0])
                else:
                    raise UnknownCollection
            else:
                raise InvalidURN

        try:
            text = self.inventory[str(urn)]
        except MyCapytain.errors.UnknownCollection as E:
            raise UnknownCollection(str(E))
        except Exception as E:
            raise E

        resource = self.read(identifier=urn, path=text.path)

        return resource, text

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: Object Identifier to filter on
        :type objectId: str
        :param filters: Kwargs parameters.
        :type filters: dict
        :return: Collection
        """
        return self.get_or(
            _cache_key("Nautilus", self.name, "GetMetadata", objectId),
            CTSCapitainsLocalResolver.getMetadata, self, objectId
        )

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: PrototypeText Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: Passage Reference
        :type subreference: str
        :return: List of references
        :rtype: [str]
        """
        return self.get_or(
            _cache_key("Nautilus", self.name, "getReffs", textId, level, subreference),
            CTSCapitainsLocalResolver.getReffs, self, textId, level, subreference
        )

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: PrototypeText Identifier
        :type textId: str
        :param subreference: Passage Reference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: Passage
        :rtype: Passage
        """
        key = _cache_key("Nautilus", self.name, "Passage", textId, subreference)
        o = self.cache.get(key)
        if o is not None:
            return o
        text, text_metadata = self.__getText__(textId)
        if subreference is not None:
            subreference = Reference(subreference)

        passage = text.getTextualNode(subreference)
        passage.set_metadata_from_collection(text_metadata)
        self.cache.set(key, passage)
        return passage

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: PrototypeText Identifier
        :type textId: str
        :param subreference: Passage Reference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        key = _cache_key("Nautilus", self.name, "Siblings", textId, subreference)
        o = self.cache.get(key)
        if o is not None:
            return o
        passage = self.getTextualNode(textId, subreference, prevnext=True)
        siblings = passage.siblingsId
        self.cache.set(key, siblings)
        return siblings
