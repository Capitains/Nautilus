import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../.."))

subprocess_repository = ["./tests/test_data/latinLit"]
subprocess_cache_dir = "cache_dir"
http_cache_dir = "http_cache_dir"