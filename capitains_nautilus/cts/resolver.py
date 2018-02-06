import os.path
from werkzeug.contrib.cache import NullCache

import MyCapytain.errors
from MyCapytain.common.reference import URN, Reference
from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText as Text
from MyCapytain.common.constants import set_graph, get_graph
from MyCapytain.resolvers.utils import CollectionDispatcher

from capitains_nautilus import _cache_key
from capitains_nautilus.errors import *
from capitains_nautilus.cts.collections import (
    SparqlXmlCitation,
    SparqlXmlCtsEditionMetadata,
    SparqlXmlCtsTextgroupMetadata,
    SparqlXmlCtsTextInventoryMetadata,
    SparqlXmlCtsTranslationMetadata,
    SparqlXmlCtsCommentaryMetadata,
    SparqlXmlCtsWorkMetadata,
    SparqlTextInventoryCollection
)


from rdflib import URIRef, Literal, plugin, Graph
from rdflib.store import Store
from rdflib_sqlalchemy import registerplugins


class __BaseNautilusCTSResolver__(CtsCapitainsLocalResolver):
    TIMEOUT = 0
    REMOVE_EMPTY = True
    CACHE_FULL_TEI = False
    RAISE_ON_GENERIC_PARSING_ERROR = False

    def __init__(self, resource, name=None, logger=None, cache=None, dispatcher=None):
        """ Initiate the XMLResolver

        """
        super(__BaseNautilusCTSResolver__, self).__init__(
            resource=resource, dispatcher=dispatcher, name=name, logger=logger, autoparse=False
        )

        if cache is None:
            cache = NullCache()

        self.__cache__ = cache
        self.__resources__ = resource

        self.inventory_cache_key = _cache_key("Nautilus", self.name, "Inventory", "Resources")
        self.texts_parsed_cache_key = _cache_key("Nautilus", self.name, "Inventory", "TextsParsed")

    @property
    def cache(self):
        return self.__cache__

    def xmlparse(self, file):
        """ Parse a XML file

        :param file: Opened File
        :return: Tree
        """
        if self.CACHE_FULL_TEI is True:
            return self.get_or(
                _cache_key("Nautilus", self.name, "File", "Tree", file.name),
                super(__BaseNautilusCTSResolver__, self).xmlparse, file
            )
        return super(__BaseNautilusCTSResolver__, self).xmlparse(file)

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
        if self.CACHE_FULL_TEI is True:
            o = self.cache.get(_cache_key(self.texts_parsed_cache_key, identifier))
            if o is not None:
                return o
            else:
                with open(path) as f:
                    o = Text(urn=identifier, resource=self.xmlparse(f))
                    self.cache.set(_cache_key(self.texts_parsed_cache_key, identifier), o)
        else:
            with open(path) as f:
                o = Text(urn=identifier, resource=self.xmlparse(f))
        return o

    def parse(self, resource=None):
        """ Parse a list of directories ans

        :param resource: List of folders
        """
        if resource is None:
            resource = self.__resources__

        try:
            inventory = super(__BaseNautilusCTSResolver__, self).parse(resource=resource)
        except MyCapytain.errors.UndispatchedTextError as E:
            if self.RAISE_ON_UNDISPATCHED is True:
                raise UndispatchedTextError(E)

        for removable in self.invalid_collections:
            if removable in self.dispatcher.collection:
                del self.dispatcher.collection[removable]

        removing = []

        if self.REMOVE_EMPTY is True:
            # Find resource with no readable descendants
            for item in self.dispatcher.collection.descendants:
                if not item.readable and len(item.readableDescendants) == 0:
                    removing.append(item.id)

            # Remove them only if they have not been removed before
            for removable in removing:
                if removable in self.dispatcher.collection:
                    del self.dispatcher.collection[removable]

        self.inventory = self.dispatcher.collection
        return self.inventory

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
                    for t in self.texts
                    if t.id.startswith(str(urn)) and isinstance(t, self.classes["edition"])
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

        if os.path.isfile(text.path):
            resource = self.read(identifier=urn, path=text.path)
        else:
            raise UnknownCollection("File matching %s does not exist" % text.path)

        return resource, text

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
            self.__cache_key_reffs__(textId, level, subreference),
            super(__BaseNautilusCTSResolver__, self).getReffs, textId, level, subreference
        )

    def __cache_key_reffs__(self, textId, level, subreference):
        return _cache_key("Nautilus", self.name, "getReffs", textId, level, subreference)

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


class NautilusCTSResolver(__BaseNautilusCTSResolver__):
    """ XML Folder Based resolver fully cache oriented (including the inventory)

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]
    :param name: Key used to make cache key
    :param cache: Cache object to be used for the inventory
    :type cache: BaseCache
    :param logger: Logging object
    :type logger: logging.logger

    :ivar inventory_cache_key: Werkzeug Cache key to get or set cache for the TextInventory
    :ivar texts_cache_key:  Werkzeug Cache key to get or set cache for lists of metadata texts objects
    :ivar texts_parsed:  Werkzeug Cache key to get or set cache for lists of parsed texts objects
    :ivar texts: List of Text Metadata objects
    :ivar source: Original resource parameter

    .. warning :: This resolver does not support inventories
    """

    @property
    def inventory(self):
        if self.__inventory__ is None or len(self.__inventory__.readableDescendants) == 0:
            self.__inventory__ = self.get_or(self.inventory_cache_key, self.parse, self.__resources__)
            set_graph(self.__inventory__.graph)
        return self.__inventory__

    @inventory.setter
    def inventory(self, value):
        self.__inventory__ = value
        self.cache.set(self.inventory_cache_key, value, self.TIMEOUT)

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
            super(__BaseNautilusCTSResolver__, self).getMetadata, objectId
        )


class SparqlAlchemyNautilusCTSResolver(__BaseNautilusCTSResolver__):
    RAISE_ON_GENERIC_PARSING_ERROR = False
    CLASSES = {
        "edition": SparqlXmlCtsEditionMetadata,
        "translation": SparqlXmlCtsTranslationMetadata,
        "commentary": SparqlXmlCtsCommentaryMetadata,
        "work": SparqlXmlCtsWorkMetadata,
        "textgroup": SparqlXmlCtsTextgroupMetadata,
        "inventory": SparqlXmlCtsTextInventoryMetadata,
        "inventory_collection": SparqlTextInventoryCollection,
        "citation": SparqlXmlCitation
    }

    def __init__(self, resource, name=None, logger=None, cache=None, dispatcher=None, sqlalchemy_address=None):
        exceptions = []
        if sqlalchemy_address:
            registerplugins()
            self.ident = URIRef("NautilusSparql")
            self.uri = Literal(sqlalchemy_address)
            store = plugin.get("SQLAlchemy", Store)(identifier=self.ident)
            self.graph = Graph(store, identifier=self.ident)
            self.graph.open(self.uri, create=True)

        if not dispatcher:
            # Normal init is setting label automatically
            inventory_collection = type(self).CLASSES["inventory_collection"](identifier="defaultTic")
            ti = type(self).CLASSES["inventory"]("default")
            ti.parent = inventory_collection
            try:
                ti.set_label("Default collection", "eng")
            except Exception:
                exceptions = ["Label was already set on the default dispatcher"]
            dispatcher = CollectionDispatcher(inventory_collection)
            
        super(SparqlAlchemyNautilusCTSResolver, self).__init__(
            resource=resource,
            name=name,
            logger=logger,
            cache=cache,
            dispatcher=dispatcher
        )

        for exception in exceptions:
            self.logger.warning(exception)

    @property
    def graph(self):
        return get_graph()

    @graph.setter
    def graph(self, value):
        set_graph(value)

    @property
    def inventory(self):
        return self.dispatcher.collection

    @inventory.setter
    def inventory(self, value):
        pass

    def clear(self):
        """ Deletes the database

        :return:
        """
        self.graph.destroy(self.uri)
        try:
            self.graph.close()
        except:
            pass

