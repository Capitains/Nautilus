from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache
from tests.cts.config import subprocess_repository, subprocess_cache_dir, sqlite_address

cache = FileSystemCache(subprocess_cache_dir)
resolver = SparqlAlchemyNautilusCTSResolver(
    resource=subprocess_repository,
    cache=cache,
    sqlalchemy_address=sqlite_address
)
resolver.parse()