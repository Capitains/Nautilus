class InventoryResolver(object):
    ALL_PAGE = None
    DEFAULT_PAGE = None

    def __init__(self, resource):
        self.resource = resource

    def cache(self, fn):
        raise NotImplemented

    def resetCache(self):
        raise NotImplemented

    def get(self, urn=None, page=None, limit=None, inventory=None, lang=None, type=None):
        raise NotImplemented
