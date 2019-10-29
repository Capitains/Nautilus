from pkg_resources import resource_filename
import logging
from copy import deepcopy
from collections import defaultdict

from flask import Blueprint, Response


from capitains_nautilus.apis.cts import CTSApi
from capitains_nautilus.apis.dts import DTSApi


def _all_origins():
    return "*"


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
    :param apis: Set of APIs to connect to Nautilus
    :type apis: set of classes

    :cvar ROUTES: List of triple length tuples
    :cvar Access_Control_Allow_Methods: Dictionary with route name and allowed methods over CORS
    :cvar Access_Control_Allow_Origin: Dictionary with route name and allowed host over CORS or "*"
    :cvar LoggingHandler: Logging handler to be set for the blueprint
    :ivar logger: Logging handler
    :type logger: logging.Logger

    :ivar resolver: CapiTainS resolver
    """
    Access_Control_Allow_Origin = "*"
    LoggingHandler = logging.StreamHandler

    def __init__(self, prefix="", app=None, name=None,
                 resolver=None,
                 flask_caching=None,
                 access_Control_Allow_Origin=None,
                 access_Control_Allow_Methods=None,
                 logger=None, apis=None
        ):
        self._extensions = {}
        self.logger = None
        self.retriever = None

        self.resolver = resolver

        self.setLogger(logger)

        self.name = name
        self.prefix = prefix
        self.blueprint = None

        self.ROUTES = []
        self.CACHED = []

        self.routes = []

        if apis is None:
            from warnings import warn
            warn(
                "The parameter `apis` will need to be set-up explicitly starting 2.0.0",
                DeprecationWarning
            )
            apis = {CTSApi(), DTSApi()}

        self.Access_Control_Allow_Methods = access_Control_Allow_Methods
        if not self.Access_Control_Allow_Methods:
            self.Access_Control_Allow_Methods = {}

        if access_Control_Allow_Origin:
            self.Access_Control_Allow_Origin = defaultdict(_all_origins)
            self.Access_Control_Allow_Origin.update(access_Control_Allow_Origin)
        else:
            self.Access_Control_Allow_Origin = FlaskNautilus.Access_Control_Allow_Origin

        for api in apis:
            api.init_extension(self)

        self.__flask_caching__ = flask_caching

        if self.name is None:
            self.name = __name__

        if app:
            self.init_app(app=app)

    def register(self, extension, extension_name):
        """ Register an extension into the Nautilus Router

        :param extension: Extension
        :param extension_name: Name of the Extension
        :return:
        """
        self._extensions[extension_name] = extension
        self.ROUTES.extend([
            tuple(list(t) + [extension_name])
            for t in extension.ROUTES
        ])
        self.CACHED.extend([
            (f_name, extension_name)
            for f_name in extension.CACHED
        ])

        # This order allows for user defaults to overwrite extension ones
        self.Access_Control_Allow_Methods.update({
            k: v
            for k, v in extension.Access_Control_Allow_Methods.items()
            if k not in self.Access_Control_Allow_Methods
        })

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

        self.init_blueprint(app)

        if self.flaskcache is not None:
            for func, extension_name in self.CACHED:
                func = getattr(self._extensions[extension_name], func)
                setattr(
                    self._extensions[extension_name],
                    func.__name__,
                    self.flaskcache.memoize()(func)
                )

        return self.blueprint

    def init_blueprint(self, app):
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
        for url, name, methods, extension_name in self.ROUTES:
            self.blueprint.add_url_rule(
                url,
                view_func=self.view(name, extension_name),
                endpoint=name[2:],
                methods=methods
            )

        app.register_blueprint(self.blueprint)
        return self.blueprint

    def view(self, function_name, extension_name):
        """ Builds response according to a function name

        :param function_name: Route name / function name
        :param extension_name: Name of the extension holding the function
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
            val = getattr(self._extensions[extension_name], function_name)(*x, **y)
            if isinstance(val, Response):
                val.headers.extend(d)
                return val
            else:
                val = list(val)
                val[2].update(d)
                return tuple(val)
        return r
