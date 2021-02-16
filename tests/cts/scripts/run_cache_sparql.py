import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCtsResolver
from cachelib import FileSystemCache
from tests.cts.config import subprocess_repository, subprocess_cache_dir, sqlite_address

cache = FileSystemCache(subprocess_cache_dir)
resolver = SparqlAlchemyNautilusCtsResolver(
    resource=subprocess_repository,
    cache=cache,
    graph=sqlite_address
)
resolver.parse()
