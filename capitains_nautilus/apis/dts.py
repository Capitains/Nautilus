from flask import jsonify, request

from MyCapytain.common.constants import Mimetypes

from capitains_nautilus.apis.base import AdditionalAPIPrototype
from capitains_nautilus.errors import NautilusError


class DTSApi(AdditionalAPIPrototype):
    ROUTES = [
        ('/dts/collections', "r_dts_collection", ["GET", "OPTIONS"]),
        ('/dts/collections/<objectId>', "r_dts_collections", ["GET", "OPTIONS"])
    ]
    Access_Control_Allow_Methods = {
        "r_dts_collection": "OPTIONS, GET",
        "r_dts_collections": "OPTIONS, GET"
    }
    CACHED = [
        #  DTS
        "r_dts_collections", "r_dts_collection", "dts_error"
    ]

    def dts_error(self, error_name, message=None):
        """ Create a DTS Error reply

        :param error_name: Name of the error
        :param message: Message of the Error
        :return: DTS Error Response with information (JSON)
        """
        self.logger.info("DTS error thrown {} for {} ({})".format(error_name, request.path, message))
        j = jsonify({
                "error": error_name,
                "message": message
            })
        j.status_code = 404
        return j

    def r_dts_collection(self, objectId=None):
        """ DTS Collection Metadata reply for given objectId

        :param objectId: Collection Identifier
        :return: JSON Format of DTS Collection
        """
        try:
            j = self.resolver.getMetadata(objectId=objectId).export(Mimetypes.JSON.DTS.Std)
            j = jsonify(j)
            j.status_code = 200
        except NautilusError as E:
            return self.dts_error(error_name=E.__class__.__name__, message=E.__doc__)
        return j

    def r_dts_collections(self, objectId):
        """ DTS Collection Metadata reply for given objectId

        :param objectId: Collection Identifier
        :return: JSON Format of DTS Collection
        """
        return self.r_dts_collection(objectId)
