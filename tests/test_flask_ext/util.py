import urltools


def normalize_uri_string(uri: str) -> str:
    suffix = ""
    if "{" in uri:
        _index = uri.index("{")
        uri, suffix = uri[:_index], uri[_index:]

    return urltools.normalize(uri)+suffix


def normalize_uri_key(obj, key):
    obj[key] = normalize_uri_string(obj[key])
