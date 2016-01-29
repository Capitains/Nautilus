# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

from flask import Flask, Blueprint, request
from flask_cache import Cache
from flask_compress import Compress
from werkzeug.contrib.cache import BaseCache, NullCache

from nautilus.mycapytain import Text, NautilusEndpoint


class FlaskNautilus(object):
    ROUTES = [
        ('/', "r_dispatcher", ["GET"])
    ]

    def __init__(self,
        prefix="", app=None, name=None,
        resources=[], parser_cache=None,
        compresser=True,
        http_cache=None, pagination=False
    ):
        """ Initiate the class

        :param prefix: Prefix on which to install the extension
        :param app: Application on which to register
        :param name: Name to use for the blueprint
        :param resources: List of directory to feed the inventory
        :type resource: list(str)
        :param parser_cache:
        :param http_cache: HTTP Cache should be a FlaskCache object
        """

        # Set up endpoints with cache system
        self.endpoint = NautilusEndpoint(resources, pagination=pagination)
        if parser_cache:
            Text.CACHE_CLASS = parser_cache
        self.endpoint.resolver.TEXT_CLASS = Text

        self.app = app
        self.name = name
        self.prefix = prefix
        self.blueprint = None
        self.__http_cache = http_cache

        self.__compresser = False

        if self.name is None:
            self.name = __name__

        if self.app:
            self.init_app(app=app, compresser=compresser)

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
                view_func=getattr(self, name),
                endpoint=name[2:],
                methods=methods
            )

        self.app.register_blueprint(self.blueprint)

    def r_dispatcher(self):
        """ Actual main route of CTS APIs

        :return: Response
        """
        _request = request.args.get("request", None)
        if not _request:
            return "This request does not exist", 404, ""  # Should maybe return documentation on top of 404 ?
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
        return self.endpoint.getCapabilities(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}

    def _r_GetPassage(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPassage(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}

    def _r_GetPassagePlus(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPassagePlus(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}

    def _r_GetValidReff(self, urn, inv, level):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getValidReff(inventory=inv, urn=urn, level=level).strip(), 200, {"content-type": "text/xml"}

    def _r_GetPrevNext(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getPrevNextUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}

    def _r_GetFirstUrn(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getFirstUrn(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}

    def _r_GetLabel(self, urn, inv):
        """

        :param urn:
        :return:
        """
        return self.endpoint.getLabel(inventory=inv, urn=urn).strip(), 200, {"content-type": "text/xml"}
