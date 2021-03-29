# -*- coding: utf-8 -*-

from flask import Flask
from cachelib import FileSystemCache
from flask_caching import Cache
from tests.test_cli.config import subprocess_repository, subprocess_cache_dir, http_cache_dir


from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection, CtsTextInventoryMetadata
from MyCapytain.resolvers.utils import CollectionDispatcher
from capitains_nautilus.cts.resolver import NautilusCtsResolver

from capitains_nautilus.flask_ext import FlaskNautilus


def make_dispatcher():
    tic = CtsTextInventoryCollection()
    latin = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
    latin.set_label("Classical Latin", "eng")
    latin.set_label("Latin Classique", "fre")
    dispatcher = CollectionDispatcher(tic)

    @dispatcher.inventory("urn:perseus:latinLit")
    def dispatchLatinLit(collection, path=None, **kwargs):
        if collection.id.startswith("urn:cts:latinLit:"):
            return True
        return False

    return dispatcher


nautilus_cache = FileSystemCache(subprocess_cache_dir, default_timeout=0)

resolver = NautilusCtsResolver(
    subprocess_repository,
    dispatcher=make_dispatcher(),
    cache=nautilus_cache
)

app = Flask("Nautilus")
http_cache = Cache(
    app,
    config={
        'CACHE_TYPE': "filesystem",
        "CACHE_DIR": http_cache_dir,
        "CACHE_DEFAULT_TIMEOUT": 0
    }
)
nautilus = FlaskNautilus(
    app=app,
    prefix="/api",
    name="nautilus",
    resolver=resolver,
    flask_caching=http_cache
)

#http_cache.init_app(app)
app.debug = True

#if __name__ == "__main__":
#    app.run(debug=True, host='0.0.0.0')
