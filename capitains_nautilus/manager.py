import click
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
import logging


def FlaskNautilusManager(resolver, flask_nautilus):
    """ Provides a manager for flask scripts to perform specific maintenance operations

    :param resolver: Nautilus Extension Instance
    :type resolver: NautilusCTSResolver
    :param flask_nautilus: Flask Application
    :type flask_nautilus: FlaskNautilus
    :return: CLI
    :rtype: click.group

    Import with

    .. code-block:: python
        :lineno:

        from capitains_nautilus.manager import FlaskNautilusManager
        manager = FlaskNautilusManager(resolver, flask_nautilus, app)  # Where app is the name of your app

        if __name__ == "__main__":
            manager()

    """

    app = flask_nautilus.app

    @click.group()
    def CLI():
        """ CLI for Flask Nautilus """
        click.echo("Command Line Interface of Flask")

    @CLI.command()
    def flush_resolver():
        """ Flush the resolver cache system """
        if resolver.cache.clear() == True:
            click.echo("Caching of Resolver Cleared")
            resolver.__texts__ = []
            resolver.__inventory__ = type(resolver.__inventory__)(resolver.__inventory__.id)

    @CLI.command()
    def flush_http_cache():
        """ Flush the http cache

        Warning : Might flush other Flask Caching data !
        """
        flask_nautilus.flaskcache.clear()

    @CLI.command()
    def flush():
        """ Flush all caches """
        flush_http_cache()
        flush_resolver()

    @CLI.command()
    def parse():
        """ Preprocess the inventory and cache it """
        resolver.logger.setLevel(logging.INFO)
        ret = resolver.parse(ret="texts")
        click.echo("Preprocessed %s texts" % len(ret))

    @CLI.command()
    def reset():
        """ Clean then parse the inventory """
        flush()
        parse()

    return CLI
