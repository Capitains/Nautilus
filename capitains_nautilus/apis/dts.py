from flask import jsonify, request

from rdflib.namespace import DC
from MyCapytain.common.constants import get_graph

from collections import defaultdict

from capitains_nautilus.apis.base import AdditionalAPIPrototype
from capitains_nautilus.errors import NautilusError


def _resource_type(collection):
    if collection.readable:
        return "Resource"
    return "Collection"


def _json_ld_value(obj):
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
    return output


class DTSApi(AdditionalAPIPrototype):
    NAME = "DTS"
    ROUTES = [
        ('/dts/collections', "r_dts_collection", ["GET", "OPTIONS"])
    ]
    Access_Control_Allow_Methods = {
        "r_dts_collection": "OPTIONS, GET"
    }
    CACHED = [
        #  DTS
        "r_dts_collection",
        "dts_error"
    ]

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

    def r_dts_collection(self):
        """ DTS Collection Metadata reply for given objectId

        :param objectId: Collection Identifier
        :return: JSON Format of DTS Collection
        """
        objectId = request.args.get("id", None)
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
                "@id": collection.id,
                "@type": _resource_type(collection),
                "title": collection.get_label(),
                "totalItems": collection.size,
                "members": [
                    {
                        "@id": member.id,
                        "@type": _resource_type(member),
                        "title": member.get_label()
                    }
                    for member in collection.members
                ]
            }
            dc = _dc_dictionary(triples)
            if len(dc):
                j["dts:dublincore"] = dc

        except NautilusError as E:
            return self.dts_error(error_name=E.__class__.__name__, message=E.__doc__)
        j = jsonify(j)
        j.status_code = 200
        return j
