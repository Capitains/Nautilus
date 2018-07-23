import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

from capitains_nautilus.cts.resolver import NautilusCtsResolver
from werkzeug.contrib.cache import FileSystemCache
from tests.cts.config import subprocess_repository, subprocess_cache_dir

cache = FileSystemCache(subprocess_cache_dir)
resolver = NautilusCtsResolver(resource=subprocess_repository, cache=cache)
resolver.parse()
