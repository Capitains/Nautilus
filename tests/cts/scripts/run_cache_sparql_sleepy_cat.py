import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

from capitains_nautilus.cts.resolver import SleepyCatCtsResolver
from cachelib import FileSystemCache
from tests.cts.config import subprocess_repository, subprocess_cache_dir, sleepy_cat_address

cache = FileSystemCache(subprocess_cache_dir)
resolver = SleepyCatCtsResolver(
    resource=subprocess_repository,
    cache=cache,
    graph=sleepy_cat_address
)
resolver.parse()
