from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache
from tests.cts.config import subprocess_repository, subprocess_cache_dir

cache = FileSystemCache(subprocess_cache_dir)
resolver = NautilusCTSResolver(resource=subprocess_repository, cache=cache)
resolver.parse()
