from pkg_resources import resource_filename
import logging

from flask import Blueprint, Response


from capitains_nautilus.apis.cts import CTSApi
from capitains_nautilus.apis.dts import DTSApi


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
    ROUTES = []
    CACHED = []
    Access_Control_Allow_Methods = {}
    Access_Control_Allow_Origin = "*"
    LoggingHandler = logging.StreamHandler

    def __init__(self, prefix="", app=None, name=None,
                 resolver=None,
                 flask_caching=None,
                 access_Control_Allow_Origin=None,
                 access_Control_Allow_Methods=None,
                 logger=None, apis=None
        ):
        self.logger = None
        self.retriever = None

        self.resolver = resolver

        self.setLogger(logger)

        self.name = name
        self.prefix = prefix
        self.blueprint = None

        self.routes = []

        if apis is None:
            from warnings import warn
            warn(
                "The parameter apis will need to be set-up explicitely startin 2.0.0",
                DeprecationWarning
            )
            self.apis = {CTSApi(self), DTSApi(self)}

        self.Access_Control_Allow_Methods = access_Control_Allow_Methods
        if not self.Access_Control_Allow_Methods:
            self.Access_Control_Allow_Methods = {
                k: v
                for k, v in FlaskNautilus.Access_Control_Allow_Methods.items()
            }
        self.Access_Control_Allow_Origin = access_Control_Allow_Origin
        if not self.Access_Control_Allow_Origin:
            self.Access_Control_Allow_Origin = {
                k: v
                for k, v in FlaskNautilus.Access_Control_Allow_Origin
            }

        for api in self.apis:
            self.ROUTES.extend(api.ROUTES)
            self.CACHED.extend(api.CACHED)
            self.Access_Control_Allow_Methods.update(api.Access_Control_Allow_Methods)

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

        self.init_blueprint(app)

        if self.flaskcache is not None:
            for func in self.CACHED:
                func = getattr(self, func)
                setattr(self, func.__name__, self.flaskcache.memoize()(func))
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
        for url, name, methods in self.ROUTES:
            self.blueprint.add_url_rule(
                url,
                view_func=self.view(name),
                endpoint=name[2:],
                methods=methods
            )

        app.register_blueprint(self.blueprint)
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
