from pkg_resources import resource_filename
import logging

from flask import Blueprint, request, render_template, Markup, jsonify, Response

from MyCapytain.common.constants import Mimetypes, RDF_NAMESPACES
from MyCapytain.common.reference import URN

from capitains_nautilus.errors import NautilusError, MissingParameter, InvalidURN


class FlaskNautilus(object):
    """ HTTP API Interfaces for MyCapytains resolvers

    :param prefix: Prefix on which to install the extension
    :param app: Application on which to register
    :param name: Name to use for the blueprint
    :param resolver: Resolver
    :type resolver: Resolver
    :param flask_caching: HTTP Cache should be a FlaskCaching Cache object
    :type flask_caching: Cache
    :cvar access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :param logger: Logging handler.
    :type logger: logging

    :cvar ROUTES: List of triple length tuples
    :cvar Access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar Access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :cvar LoggingHandler: Logging handler to be set for the blueprint
    :ivar logger: Logging handler
    :type logger: logging.Logger

    :ivar resolver: CapiTainS resolver
    """
    ROUTES = [
        ('/cts', "r_cts", ["GET"]),
        ('/dts/collections', "r_dts_collection", ["GET", "OPTIONS"]),
        ('/dts/collections/<objectId>', "r_dts_collections", ["GET", "OPTIONS"])
        #('/sparql', "r_sparql", ["GET"])
    ]
    Access_Control_Allow_Methods = {
        "r_cts": "OPTIONS, GET",
        "r_dts_collection": "OPTIONS, GET",
        "r_dts_collections": "OPTIONS, GET"
    }
    Access_Control_Allow_Origin = "*"
    LoggingHandler = logging.StreamHandler
    CACHED = [
        #  CTS
        "_r_GetCapabilities", "_r_GetPassage", "_r_GetPassagePlus",
        "_r_GetValidReff", "_r_GetPrevNext", "_r_GetFirstUrn", "_r_GetLabel",
        "cts_error",
        #  DTS
        "r_dts_collections", "r_dts_collection", "dts_error"
    ]

    def __init__(self, prefix="", app=None, name=None,
                 resolver=None,
                 flask_caching=None,
                 access_Control_Allow_Origin=None,
                 access_Control_Allow_Methods=None,
                 logger=None
        ):
        self.logger = None
        self.retriever = None

        self.resolver = resolver

        self.setLogger(logger)

        self.app = app
        self.name = name
        self.prefix = prefix
        self.blueprint = None

        self.Access_Control_Allow_Methods = access_Control_Allow_Methods
        if not self.Access_Control_Allow_Methods:
            self.Access_Control_Allow_Methods = FlaskNautilus.Access_Control_Allow_Methods
        self.Access_Control_Allow_Origin = access_Control_Allow_Origin
        if not self.Access_Control_Allow_Origin:
            self.Access_Control_Allow_Origin = FlaskNautilus.Access_Control_Allow_Origin

        self.__flask_caching__ = flask_caching

        if self.name is None:
            self.name = __name__

        if self.app:
            self.init_app(app=app)

    @property
    def flaskcache(self):
        return self.__flask_caching__

    def setLogger(self, logger):
        """ Set up the Logger for the application

        :param logger: logging.Logger object
        :return: Logger instance
        """
        self.logger = logger
        if logger is None:
            self.logger = logging.getLogger("capitains_nautilus")
            formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
            stream = FlaskNautilus.LoggingHandler()
            stream.setLevel(logging.INFO)
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)

        if self.resolver:
            self.resolver.logger = self.logger

        return self.logger

    def init_app(self, app):
        """ Initiate the extension on the application

        :param app: Flask Application
        :return: Blueprint for Flask Nautilus registered in app
        :rtype: Blueprint
        """

        self.app = app

        self.init_blueprint()

        if self.flaskcache is not None:
            for func in self.CACHED:
                func = getattr(self, func)
                setattr(self, func.__name__, self.flaskcache.memoize()(func))
        return self.blueprint

    def init_blueprint(self):
        """ Properly generates the blueprint, registering routes and filters and connecting the app and the blueprint

        :return: Blueprint of the extension
        :rtype: Blueprint
        """
        self.blueprint = Blueprint(
            self.name,
            self.name,
            template_folder=resource_filename("capitains_nautilus", "data/templates"),
            url_prefix=self.prefix
        )

        # Register routes
        for url, name, methods in FlaskNautilus.ROUTES:
            self.blueprint.add_url_rule(
                url,
                view_func=self.view(name),
                endpoint=name[2:],
                methods=methods
            )

        self.app.register_blueprint(self.blueprint)
        return self.blueprint

    def view(self, function_name):
        """ Builds response according to a function name

        :param function_name: Route name / function name
        :return: Function
        """
        if isinstance(self.Access_Control_Allow_Origin, dict):
            d = {
                "Access-Control-Allow-Origin": self.Access_Control_Allow_Origin[function_name],
                "Access-Control-Allow-Methods": self.Access_Control_Allow_Methods[function_name]
            }
        else:
            d = {
                "Access-Control-Allow-Origin": self.Access_Control_Allow_Origin,
                "Access-Control-Allow-Methods": self.Access_Control_Allow_Methods[function_name]
            }

        def r(*x, **y):
            val = getattr(self, function_name)(*x, **y)
            if isinstance(val, Response):
                val.headers.extend(d)
                return val
            else:
                val = list(val)
                val[2].update(d)
                return tuple(val)
        return r

    def r_cts(self):
        """ Actual main route of CTS APIs. Transfer typical requests through the ?request=REQUESTNAME route

        :return: Response
        """
        _request = request.args.get("request", None)
        if _request is not None:
            try:
                if _request.lower() == "getcapabilities":
                    return self._r_GetCapabilities(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getpassage":
                    return self._r_GetPassage(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getpassageplus":
                    return self._r_GetPassagePlus(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getlabel":
                    return self._r_GetLabel(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getfirsturn":
                    return self._r_GetFirstUrn(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getprevnexturn":
                    return self._r_GetPrevNext(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getvalidreff":
                    return self._r_GetValidReff(
                        urn=request.args.get("urn", None),
                        level=request.args.get("level", 1, type=int)
                    )
            except NautilusError as E:
                return self.cts_error(error_name=E.__class__.__name__, message=E.__doc__)
        return self.cts_error(MissingParameter.__name__, message=MissingParameter.__doc__)

    def cts_error(self, error_name, message=None):
        """ Create a CTS Error reply

        :param error_name: Name of the error
        :param message: Message of the Error
        :return: CTS Error Response with information (XML)
        """
        self.logger.info("CTS error thrown {} for {} ({})".format(error_name, request.query_string.decode(), message))
        return render_template(
            "cts/Error.xml",
            errorType=error_name,
            message=message
        ), 404, {"content-type": "application/xml"}

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

    def _r_GetCapabilities(self, urn=None):
        """ Provisional route for GetCapabilities request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetCapabilities response
        """
        r = self.resolver.getMetadata(objectId=urn)
        if len(r.parents) > 0:
            r = r.parents[-1]
        r = render_template(
            "cts/GetCapabilities.xml",
            filters="urn={}".format(urn),
            inventory=Markup(r.export(Mimetypes.XML.CTS))
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetPassage(self, urn):
        """ Provisional route for GetPassage request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPassage response
        """
        urn = URN(urn)
        subreference = None
        if len(urn) < 4:
            raise InvalidURN
        if urn.reference is not None:
            subreference = str(urn.reference)
        node = self.resolver.getTextualNode(textId=urn.upTo(URN.NO_PASSAGE), subreference=subreference)

        r = render_template(
            "cts/GetPassage.xml",
            filters="urn={}".format(urn),
            request_urn=str(urn),
            full_urn=node.urn,
            passage=Markup(node.export(Mimetypes.XML.TEI))
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetPassagePlus(self, urn):
        """ Provisional route for GetPassagePlus request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPassagePlus response
        """
        urn = URN(urn)
        subreference = None
        if len(urn) < 4:
            raise InvalidURN
        if urn.reference is not None:
            subreference = str(urn.reference)
        node = self.resolver.getTextualNode(textId=urn.upTo(URN.NO_PASSAGE), subreference=subreference)
        r = render_template(
            "cts/GetPassagePlus.xml",
            filters="urn={}".format(urn),
            request_urn=str(urn),
            full_urn=node.urn,
            prev_urn=node.prevId,
            next_urn=node.nextId,
            metadata={
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.label)]
            },
            citation=Markup(node.citation.export(Mimetypes.XML.CTS)),
            passage=Markup(node.export(Mimetypes.XML.TEI))
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetValidReff(self, urn, level):
        """ Provisional route for GetValidReff request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetValidReff response
        """
        urn = URN(urn)
        subreference = None
        textId=urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        reffs = self.resolver.getReffs(textId=textId, subreference=subreference, level=level)
        r = render_template(
            "cts/GetValidReff.xml",
            reffs=reffs,
            urn=textId,
            level=level,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetPrevNext(self, urn):
        """ Provisional route for GetPrevNext request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPrevNext response
        """
        urn = URN(urn)
        subreference = None
        textId = urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        previous, nextious = self.resolver.getSiblings(textId=textId, subreference=subreference)
        r = render_template(
            "cts/GetPrevNext.xml",
            prev_urn=previous,
            next_urn=nextious,
            urn=textId,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetFirstUrn(self, urn):
        """ Provisional route for GetFirstUrn request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetFirstUrn response
        """
        urn = URN(urn)
        subreference = None
        textId = urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        firstId = self.resolver.getTextualNode(textId=textId, subreference=subreference).firstId
        r = render_template(
            "cts/GetFirstUrn.xml",
            firstId=firstId,
            full_urn=textId,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _r_GetLabel(self, urn):
        """ Provisional route for GetLabel request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetLabel response
        """
        node = self.resolver.getTextualNode(textId=urn)
        r = render_template(
            "cts/GetLabel.xml",
            request_urn=str(urn),
            full_urn=node.urn,
            metadata={
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.label)]
            },
            citation=Markup(node.citation.export(Mimetypes.XML.CTS))
        )
        return r, 200, {"content-type": "application/xml"}