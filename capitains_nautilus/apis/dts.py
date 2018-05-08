from flask import Response, request, url_for

from lxml import etree
from rdflib.namespace import DC
from rdflib import Literal, URIRef
from MyCapytain.common.constants import get_graph, \
    RDF_NAMESPACES, \
    Mimetypes, \
    XPATH_NAMESPACES

from collections import defaultdict
import json

from capitains_nautilus.apis.base import AdditionalAPIPrototype, \
    query_parameters_as_kwargs
from capitains_nautilus.errors import NautilusError


def jsonify(response):
    return Response(json.dumps(response), headers={
        "Content-Type": "application/ld+json"
    })


def _nav_direction(collection, direction):
    if direction == "children":
        return collection.members
    if direction == "parent":
        return [collection.parent]


def _resource_type(collection):
    if collection.readable:
        return "Resource"
    return "Collection"


def _json_ld_value(obj):
    if isinstance(obj, URIRef):
        return str(obj)
    if obj.language:
        return {"@lang": obj.language, "@value": str(obj)}
    return str(obj)


def _dc_dictionary(triples):
    """ Builds a dc dictionary based on the triples

    :param triples: [(pred, obj)]
    :return: Dictionary
    :rtype: dict
    """
    output = defaultdict(list)
    for pred, obj in triples:
        if pred.startswith(DC):
            *_, key = get_graph().namespace_manager.compute_qname(pred)
            output[key].append(_json_ld_value(obj))
    if output:
        output = {"dts:dublincore": output}
    return output


def _metadata(triples):
    """ Builds a dc dictionary based on the triples

    :param triples: [(pred, obj)]
    :return: Dictionary
    :rtype: dict
    """
    output = defaultdict(list)
    for pred, obj in triples:
        if not pred.startswith(DC) and not pred.startswith(RDF_NAMESPACES.DTS):
            key = get_graph().namespace_manager.qname(pred)
            output[key].append(_json_ld_value(obj))
    if output:
        output = {"dts:extensions": output}
    return output


def _base_description(collection, _external=False):
    j = {
        "@id": collection.id,
        "@type": _resource_type(collection),
        "title": collection.get_label(),
        "totalItems": collection.size,
    }
    if hasattr(collection, "get_description"):
        j["description"] = collection.get_description()
    if collection.readable:
        j["dts:passage"] = url_for(".dts_document", id=collection.id, _external=_external)
        j["dts:references"] = url_for(".dts_navigation", id=collection.id, _external=_external)
    return j


class DTSApi(AdditionalAPIPrototype):
    NAME = "DTS"
    ROUTES = [
        ('/dts/', "r_dts_main", ["GET", "OPTIONS"]),
        ('/dts/collections', "r_dts_collection", ["GET", "OPTIONS"]),
        ('/dts/document', "r_dts_document", ["GET", "OPTIONS"]),
        ('/dts/navigation', "r_dts_navigation", ["GET", "OPTIONS"])
    ]
    Access_Control_Allow_Methods = {
        "r_dts_collection": "OPTIONS, GET",
        "r_dts_main": "OPTIONS, GET",
        "r_dts_document": "OPTIONS, GET",
        "r_dts_navigation": "OPTIONS, GET"
    }
    CACHED = [
        #  DTS
        "r_dts_collection",
        "dts_error",
        "r_dts_main"
    ]

    def __init__(self, _external=False):
        super(DTSApi, self).__init__()
        self._external = _external

    def dts_error(self, error_name, message=None):
        """ Create a DTS Error reply

        :param error_name: Name of the error
        :param message: Message of the Error
        :return: DTS Error Response with information (JSON)
        """
        self.nautilus_extension.logger.info("DTS error thrown {} for {} ({})".format(
            error_name, request.path, message
        ))
        j = jsonify({
                "error": error_name,
                "message": message
            })
        j.status_code = 404
        return j

    def r_dts_main(self):
        return jsonify({
          "@context": "dts/EntryPoint.jsonld",
          "@id": "dts/",
          "@type": "EntryPoint",

          "collections": url_for(".dts_collection", _external=self._external),
          "documents": url_for(".dts_document", _external=self._external),
          "navigation": url_for(".dts_navigation", _external=self._external)
        })

    @query_parameters_as_kwargs(
        mapping={"id": "objectId", "nav": "direction"},
        params={
            "id": None,
            "nav": "children"
        }
    )
    def r_dts_collection(self, objectId, direction):
        """ DTS Collection Metadata reply for given objectId

        :return: JSON Format of DTS Collection
        """

        try:
            collection = self.resolver.getMetadata(objectId=objectId)
            triples = list(collection.graph.predicate_objects(
                    collection.asNode()
            ))
            j = {
                "@context": {
                    "@base": "http://www.w3.org/ns/hydra/context.jsonld",
                    "dc": "http://purl.org/dc/terms/",
                    "dts": "https://w3id.org/dts/api#",
                    "tei": "http://www.tei-c.org/ns/1.0",
                },
                "members": [
                    _base_description(member, _external=self._external)
                    for member in _nav_direction(collection, direction)
                ]
            }
            j.update(_base_description(collection, _external=self._external))
            j.update(_dc_dictionary(triples))
            j.update(_metadata(triples))

        except NautilusError as E:
            return self.dts_error(error_name=E.__class__.__name__, message=E.__doc__)
        j = jsonify(j)
        j.status_code = 200
        return j

    @query_parameters_as_kwargs(
        mapping={"id": "objectId", "passage": "passageId"},
        params={
            "id": None,
            "passage": None,
            "start": None,
            "end": None,
            "level": 1
        }
    )
    def r_dts_navigation(self, objectId=None, passageId=None, start=None, end=None, level=1):
        if not objectId:
            raise Exception()
        if start and end:
            # Currently hacked to work only with CTS Identifier
            # See https://github.com/Capitains/MyCapytain/issues/161
            references = self.resolver.getReffs(
                textId=objectId,
                subreference="-".join([start, end]),
                level=level
            )
        else:
            references = self.resolver.getReffs(
                textId=objectId,
                subreference=passageId,
                level=level
            )
        return jsonify({
            "@context": {
                "passage": "https://w3id.org/dts/api#passage"
            },
            "@base": url_for(".dts_document", _external=self._external),
            "@id": objectId,
            "passage": references
        })

    @query_parameters_as_kwargs(
        mapping={"id": "objectId", "passage": "passageId"},
        params={
            "id": None,
            "passage": None,
            "start": None,
            "end": None
        }
    )
    def r_dts_document(self, objectId=None, passageId=None, start=None, end=None):

        if not objectId:
            raise Exception()
        if start and end:
            # Currently hacked to work only with CTS Identifier
            # See https://github.com/Capitains/MyCapytain/issues/161
            passage = self.resolver.getTextualNode(
                textId=objectId,
                subreference="-".join([start, end])
            )
        else:
            passage = self.resolver.getTextualNode(
                textId=objectId,
                subreference=passageId
            )

        if passageId:
            inputXML = passage.export(Mimetypes.PYTHON.ETREE)
            wrapper = etree.fromstring("<dts:fragment xmlns:dts='https://w3id.org/dts/api#' />")
            for container in inputXML.xpath("//tei:text", namespaces=XPATH_NAMESPACES):
                container.getparent().append(wrapper)
                wrapper.insert(0, container)
                break
            outputXML = etree.tostring(inputXML, encoding=str)
        else:
            outputXML = passage.export(Mimetypes.XML.TEI)

        return Response(
            outputXML,
            headers={
                "Content-Type": "application/tei+xml"
            }
        )
