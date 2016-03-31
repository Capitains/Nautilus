# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str
import logging

from flask import Flask, Blueprint, request
from flask_cache import Cache
from flask_compress import Compress

from nautilus.mycapytain import Text, NautilusEndpoint


class FlaskNautilus(object):
    """ Initiate the class

    :param prefix: Prefix on which to install the extension
    :param app: Application on which to register
    :param name: Name to use for the blueprint
    :param resources: List of directory to feed the inventory
    :type resource: list(str)
    :param logger: Logging handler.
    :type logger: logging
    :param parser_cache:
    :param http_cache: HTTP Cache should be a FlaskCache object
    :cvar ROUTES: List of triple length tuples
    :cvar Access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar Access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :cvar LoggingHandler: Logging handler to be set for the blueprint
    :ivar logger: Logging handler
    :type logger: logging
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
            resources=[], parser_cache=None,
            compresser=True,
            http_cache=None, pagination=False,
            access_Control_Allow_Origin=None, access_Control_Allow_Methods=None,
            logger=None
        ):
        self.logger = None
        self.endpoint = None
        self.setLogger(logger)

        # Set up endpoints with cache system
        if parser_cache:
            Text.CACHE_CLASS = parser_cache
            self.endpoint = NautilusEndpoint(resources, pagination=pagination, cache=parser_cache, logger=self.logger)
        else:
            self.endpoint = NautilusEndpoint(resources, pagination=pagination)
        self.endpoint.resolver.TEXT_CLASS = Text

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

        :param logger:
        :return:
        """
        self.logger = logger
        if not logger:
            self.logger = logging.getLogger("nautilus")
        else:
            self.logger = self.logger.getLogger("nautilus")
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        stream = FlaskNautilus.LoggingHandler()
        stream.setLevel(logging.INFO)
        stream.setFormatter(formatter)
        self.logger.addHandler(stream)

        if self.endpoint:
            self.endpoint.logger = self.logger
            self.endpoint.resolver.logger = self.logger

    def init_app(self, app, compresser=False):
        """ Initiate the extension on the application

        :param app: Flask Application
        :return: Blueprint for HookUI registered in app
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
        """ Actual main route of CTS APIs

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

    def _r_GetCapabilities(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getCapabilities(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPassage(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPassage(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPassagePlus(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPassagePlus(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetValidReff(self, urn, inv, level):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getValidReff(inventory=inv, urn=urn, level=level).strip(), 200, {"content-type": "application/xml"}

    def _r_GetPrevNext(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPrevNextUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetFirstUrn(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getFirstUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}

    def _r_GetLabel(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getLabel(inventory=inv, urn=urn).strip(), 200, {"content-type": "application/xml"}
