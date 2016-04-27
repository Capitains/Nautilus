# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from flask import Blueprint, request
from flask_cache import Cache
from flask_compress import Compress
from flask.ext.script import Manager

from capitains_nautilus.cache import BaseCache
from capitains_nautilus.mycapytain import Text, NautilusRetriever


class WerkzeugCacheWrapper(BaseCache):
    """ Werkzeug Cache Wrapper for Nautilus Base Cache object

    :param instance: Werkzeug Cache instance

    """
    def __init__(self, instance=None, *args, **kwargs):
        super(WerkzeugCacheWrapper, self).__init__(*args, **kwargs)

        if not instance:
            instance = BaseCache()
        self.__instance__ = instance

    def get(self, key):
        return self.__instance__.get(key)

    def set(self, key, value, timeout=None):
        return self.__instance__.set(key, value, timeout)

    def add(self, key, value, timeout=None):
        return self.__instance__.add(key, value, timeout)

    def clear(self):
        return self.__instance__.clear()

    def delete(self, key):
        return self.__instance__.delete(key)


class FlaskNautilus(object):
    """ Initiate the class

    :param prefix: Prefix on which to install the extension
    :param app: Application on which to register
    :param name: Name to use for the blueprint
    :param resources: List of directory to feed the inventory
    :type resources: list(str)
    :param logger: Logging handler.
    :type logger: logging
    :param parser_cache: Cache object
    :type parser_cache: BaseCache
    :param http_cache: HTTP Cache should be a FlaskCache object
    :param auto_parse: Parses on first execution the resources given to build inventory. Not recommended for production

    :cvar ROUTES: List of triple length tuples
    :cvar Access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar Access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :cvar LoggingHandler: Logging handler to be set for the blueprint
    :ivar logger: Logging handler
    :type logger: logging
    :ivar retriever: CapiTainS Retriever
    """
    ROUTES = [
        ('/', "r_dispatcher", ["GET"])
    ]
    Access_Control_Allow_Methods = {
        "r_dispatcher": "OPTIONS, GET"
    }
    Access_Control_Allow_Origin = "*"
    LoggingHandler = logging.StreamHandler

    def __init__(self,
            prefix="", app=None, name=None,
            resources=None, parser_cache=None,
            compresser=True,
            http_cache=None, pagination=False,
            access_Control_Allow_Origin=None, access_Control_Allow_Methods=None,
            logger=None,
            auto_parse=True
        ):
        self.logger = None
        self.retriever = None
        self.setLogger(logger)

        if not resources:
            resources = list()

        # Set up endpoints with cache system
        if parser_cache:
            Text.CACHE_CLASS = parser_cache
            self.retriever = NautilusRetriever(resources, pagination=pagination, cache=parser_cache, logger=self.logger, auto_parse=auto_parse)
        else:
            self.retriever = NautilusRetriever(resources, pagination=pagination, auto_parse=auto_parse)
        self.retriever.resolver.TEXT_CLASS = Text

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

        self.__http_cache = http_cache

        self.__compresser = False

        if self.name is None:
            self.name = __name__

        if self.app:
            self.init_app(app=app, compresser=compresser)

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

        if self.retriever:
            self.retriever.logger = self.logger
            self.retriever.resolver.logger = self.logger

        return self.logger

    def init_app(self, app, compresser=False):
        """ Initiate the extension on the application

        :param app: Flask Application
        :return: Blueprint for Flask Nautilus registered in app
        :rtype: Blueprint
        """

        if not self.app:
            self.app = app

        if not self.__http_cache:
            self.__http_cache = Cache(config={'CACHE_TYPE': 'simple'})

        self.init_blueprint()

        if compresser:
            self.__compresser = Compress(app)

        return self.blueprint

    def init_blueprint(self):
        """ Properly generates the blueprint, registering routes and filters and connecting the app and the blueprint

        :return: Blueprint of the extension
        :rtype: Blueprint
        """
        self.blueprint = Blueprint(
            self.name,
            self.name,
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
            val = list(getattr(self, function_name)(*x, **y))
            val[2].update(d)
            return tuple(val)
        return r

    def r_dispatcher(self):
        """ Actual main route of CTS APIs. Transfer typical requests through the ?request=REQUESTNAME route

        :return: Response
        """
        _request = request.args.get("request", None)
        if not _request:
            return "This request does not exist", 404, dict()  # Should maybe return documentation on top of 404 ?
        elif _request.lower() == "getcapabilities":
            return self._r_GetCapabilities(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getpassage":
            return self._r_GetPassage(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getpassageplus":
            return self._r_GetPassagePlus(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getlabel":
            return self._r_GetLabel(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getfirsturn":
            return self._r_GetFirstUrn(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getprevnexturn":
            return self._r_GetPrevNext(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None)
            )
        elif _request.lower() == "getvalidreff":
            return self._r_GetValidReff(
                urn=request.args.get("urn", None),
                inv=request.args.get("inv", None),
                level=request.args.get("level", 1, type=int)
            )
        return "This request does not exist", 404, ""  # Should maybe return documentation on top of 404 ?

    def _r_GetCapabilities(self, urn=None, inv=None):
        """ Provisional route for GetCapabilities request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetCapabilities response
        """
        return self.retriever.getCapabilities(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPassage(self, urn, inv):
        """ Provisional route for GetPassage request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPassage response
        """
        return self.retriever.getPassage(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPassagePlus(self, urn, inv):
        """ Provisional route for GetPassagePlus request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPassagePlus response
        """
        return self.retriever.getPassagePlus(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetValidReff(self, urn, inv, level):
        """ Provisional route for GetValidReff request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetValidReff response
        """
        return self.retriever.getValidReff(inventory=inv, urn=urn, level=level).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPrevNext(self, urn, inv):
        """ Provisional route for GetPrevNext request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPrevNext response
        """
        return self.retriever.getPrevNextUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetFirstUrn(self, urn, inv):
        """ Provisional route for GetFirstUrn request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetFirstUrn response
        """
        return self.retriever.getFirstUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetLabel(self, urn, inv):
        """ Provisional route for GetLabel request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetLabel response
        """
        return self.retriever.getLabel(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}


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
