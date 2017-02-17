from pkg_resources import resource_filename
import logging

from flask import Blueprint, request, render_template, Markup
from flask.ext.script import Manager

from capitains_nautilus.cache import BaseCache, WerkzeugCacheWrapper
from capitains_nautilus.errors import NautilusError, MissingParameter, InvalidURN
from MyCapytain.common.constants import Mimetypes, NAMESPACES
from MyCapytain.common.reference import URN


class FlaskNautilus(object):
    """ Initiate the class

    :param prefix: Prefix on which to install the extension
    :param app: Application on which to register
    :param name: Name to use for the blueprint
    :param resources: List of directory to feed the inventory
    :type resources: list(str)
    :param logger: Logging handler.
    :type logger: logging
    :param parser_cache: Cache object for resource
    :type parser_cache: BaseCache
    :param http_cache: HTTP Cache should be a FlaskCaching Cache object

    :cvar ROUTES: List of triple length tuples
    :cvar Access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar Access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :cvar LoggingHandler: Logging handler to be set for the blueprint
    :ivar logger: Logging handler
    :type logger: logging

    :ivar resolver: CapiTainS resolver
    """
    ROUTES = [
        ('/cts', "r_cts", ["GET"]),
        #('/sparql', "r_sparql", ["GET"])
    ]
    Access_Control_Allow_Methods = {
        "r_cts": "OPTIONS, GET"
    }
    Access_Control_Allow_Origin = "*"
    LoggingHandler = logging.StreamHandler
    CACHED = [
        #  CTS
        "_r_GetCapabilities", "_r_GetPassage", "_r_GetPassagePlus",
        "_r_GetValidReff", "_r_GetPrevNext", "_r_GetFirstUrn", "_r_GetLabel",
        "cts_error"
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
        if not logger:
            self.logger = logging.getLogger("capitains_nautilus")
        else:
            self.logger = self.logger.getLogger("capitains_nautilus")
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
            if isinstance(val, str):
                val.headers.update(d)
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
        return render_template(
            "cts/Error.xml",
            errorType=error_name,
            message=message
        ), 404, {"content-type": "application/xml"}

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
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.label)]
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
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get_all(NAMESPACES.CTS.label)]
            },
            citation=Markup(node.citation.export(Mimetypes.XML.CTS))
        )
        return r, 200, {"content-type": "application/xml"}


def FlaskNautilusManager(nautilus, app=None):
    """ Provides a manager for flask scripts to perform specific maintenance operations

    :param nautilus: Nautilus Extension Instance
    :param app: Flask Application
    :return: Sub-Manager
    :rtype: Manager

    Import with

    .. code-block:: python
        :lineno:

        manager = Manager(app)  # Where app is the name of your app
        from capitains_nautilus.flask_ext import manager as nautilus_manager
        manager.add_command("nautilus", FlaskNautilusManager(nautilus, app))  # Where nautilus is an instance of FlaskNautilus

    """
    _manager = Manager(usage="Perform maintenance operations")

    @_manager.command
    def flush():
        """ Flush the cache system [Right now flushes only the inventory] """
        nautilus.retriever.resolver.flush()

    @_manager.command
    def preprocess():
        """ Preprocess the inventory and cache it """
        nautilus.retriever.resolver.logger.setLevel(logging.INFO)
        nautilus.retriever.resolver.parse(resource=nautilus.retriever.resolver.source, cache=True)

    @_manager.command
    def inventory():
        """ Clean then preprocess the inventory """
        nautilus.retriever.resolver.logger.setLevel(logging.INFO)
        nautilus.retriever.resolver.flush()
        nautilus.retriever.resolver.parse(resource=nautilus.retriever.resolver.source, cache=True)

    return _manager
