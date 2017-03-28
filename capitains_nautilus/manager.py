import click
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
import logging
import multiprocessing
from multiprocessing.pool import Pool

THREADS = multiprocessing.cpu_count() - 1
if THREADS < 1:
    THREADS = 1

global NAUTILUSRESOLVER


def read_levels(text):
    """ Read text and get there reffs

    :param text: Collection (Readable)
    :return:
    """
    x = []
    for i in range(0, len(NAUTILUSRESOLVER.getMetadata(text).citation)):
        x.append(NAUTILUSRESOLVER.getReffs(text, level=i))
    return x


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
    global NAUTILUSRESOLVER
    NAUTILUSRESOLVER = resolver

    @click.group()
    @click.option('--verbose', default=False)
    def CLI(verbose):
        """ CLI for Flask Nautilus """
        click.echo("Command Line Interface of Flask")
        resolver.logger.disabled = not verbose

    @CLI.command()
    def flush_resolver():
        """ Flush the resolver cache system """
        if resolver.cache.clear() is True:
            click.echo("Caching of Resolver Cleared")

    @CLI.command()
    def flush_http_cache():
        """ Flush the http cache

        Warning : Might flush other Flask Caching data !
        """
        flask_nautilus.flaskcache.clear()

    @CLI.command()
    def flush_both():
        """ Flush all caches

        """
        if resolver.cache.clear() is True:
            click.echo("Caching of Resolver Cleared")
        if flask_nautilus.flaskcache.clear() is True:
            click.echo("Caching of HTTP Cleared")

    @CLI.command()
    def parse():
        """ Preprocess the inventory and cache it """
        ret = resolver.parse()
        click.echo("Preprocessed %s texts" % len(ret.readableDescendants))

    @CLI.command()
    @click.option('--threads', default=0, type=int)
    def process_reffs(threads):
        """ Preprocess the inventory and cache it """
        if threads < 1:
            threads = THREADS
        texts = list(resolver.getMetadata().readableDescendants)
        click.echo("Using {} processes to parse references of {} texts".format(threads, len(texts)))
        with Pool(processes=threads) as executor:
            for future in executor.imap_unordered(read_levels, [t.id for t in texts]):
                del future
        click.echo("References parsed")

    return CLI
