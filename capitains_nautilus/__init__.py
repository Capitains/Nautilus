"""
    Lilacs is a software resource to create and establish a CTS API based on Capitains Guidelines using Python
"""
__version__ = "0.0.1"


def _cache_key(*args):
    """ Cache key computing

    :param args:
    :return:
    """
    return "_".join(map(str, args))
