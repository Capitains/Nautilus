# -*- coding: utf-8 -*-

from capitains_nautilus.flask_ext import FlaskNautilus
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache, RedisCache, NullCache
from flask import Flask
import argparse
import logging

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


def _commandline(repositories,
                 port=8000, host="127.0.0.1", debug=False,
                 cache=None, cache_path="./cache", redis=None):
    """ Run a CTS API from command line.

    .. warning:: This function should not be used in the production context

    :param repositories:
    :param port:
    :param ip:
    :param debug:
    :param cache:
    :param cache_path:
    :return:
    """

    if cache == "redis":
        nautilus_cache = RedisCache(redis)
        cache_type = "redis"
    elif cache == "filesystem":
        nautilus_cache = FileSystemCache(cache_path)
        cache_type = "simple"
    else:
        nautilus_cache = NullCache()
        cache_type = "simple"

    app = Flask("Nautilus")
    if debug:
        app.logger.setLevel(logging.INFO)

    resolver = NautilusCTSResolver(resource=repositories)
    nautilus = FlaskNautilus(
        app=app,
        resolver=resolver
        #parser_cache=WerkzeugCacheWrapper(nautilus_cache),
        #logger=None
    )
    nautilus.resolver.parse()
    if debug:
        app.run(debug=debug, port=port, host=host)
    else:
        app.debug = debug
        http_server = HTTPServer(WSGIContainer(app))
        http_server.bind(port=port, address=host)
        http_server.start(0)
        IOLoop.current().start()


def cmd():
    parser = argparse.ArgumentParser(description='Capitains Nautilus CTS API')
    parser.add_argument('repositories', metavar='repository', type=str, nargs='+',
                       help='List of path to use to populate the repository')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port to use for the HTTP Server')
    parser.add_argument('--host', type=str, default="127.0.0.1",
                       help='Host to use for the HTTP Server')
    parser.add_argument("--cache", choices=["redis", "filesystem", "none"], default=None,
                        help="Cache system to use")
    parser.add_argument("--redis", default=None,
                        help="Redis address for the cache server")
    parser.add_argument("--cache_path", default="./cache",
                        help="Cache Directory Path")
    parser.add_argument('--debug', action="store_true", default=False, help="Set-up the application for debugging")

    args = parser.parse_args()

    if args.repositories:
        _commandline(**vars(args))

if __name__ == "__main__":
    cmd()
