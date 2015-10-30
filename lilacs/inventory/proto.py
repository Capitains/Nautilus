class InventoryResolver(Object):
    ALL_PAGE = None
    DEFAULT_PAGE = Resolver.ALL_PAGE
    def cache(self, fn):
        raise NotImplemented

    def resetCache(self):
        raise NotImplemented

    def get(self, urn=None, page=None, limit=None, inventory=None, lang=None, type=None):
        raise NotImplemented