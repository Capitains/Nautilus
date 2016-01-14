class InventoryResolver(object):
    ALL_PAGE = None
    DEFAULT_PAGE = None
    PER_PAGE = (1, 10, 100)  # Min, Default, Max,

    def __init__(self, resource):
        self.resource = resource
        self.__texts__ = []

    @property
    def texts(self):
        return self.__texts__

    def cache(self, fn):
        raise NotImplemented

    def resetCache(self):
        raise NotImplemented

    def get(self, urn=None, page=None, limit=None, inventory=None, lang=None, type=None):
        raise NotImplemented
