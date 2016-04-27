# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from math import ceil
from capitains_nautilus.cache import BaseCache
from MyCapytain.resources.inventory import TextInventory
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class InventoryResolver:
    """ Inventory Resolver Prototype. It is used to serve local xml files and an inventory.

    :param resource: Resource used to retrieve texts
    :param auto_parse: Automatically parse the resource on initialization

    :cvar DEFAULT_PAGE: Default Page to show
    :cvar PER_PAGE: Tuple representing the minimal number of texts returned, the default number and the maximum number of texts returned

    :ivar source: Reading access to original resource
    :ivar texts: List of MyCapytain.resources.inventory.Text


    """
    DEFAULT_PAGE = 1
    PER_PAGE = (1, 10, 100)  # Min, Default, Mainvex,

    def __init__(self, resource, auto_parse=True):
        self.__resource = resource
        self.__texts__ = []
        self.__cache = BaseCache()
        self.inventory = TextInventory()

    @property
    def source(self):
        return self.__resource

    @property
    def texts(self):
        return self.__texts__

    @abc.abstractmethod
    def cache(self, inventory, texts):
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self):
        raise NotImplementedError

    @abc.abstractmethod
    def getCapabilities(self,
            urn=None, page=None, limit=None,
            inventory=None, lang=None, category=None, pagination=True
        ):
        raise NotImplementedError

    @staticmethod
    def pagination(page, limit, length):
        """ Help for pagination

        :param page: Provided Page
        :param limit: Number of item to show
        :param length: Length of the list to paginate
        :return: (Start Index, End Index, Page Number, Item Count)
        """
        realpage = page
        page = page or InventoryResolver.DEFAULT_PAGE
        limit = limit or InventoryResolver.PER_PAGE[1]

        if limit < InventoryResolver.PER_PAGE[0] or limit > InventoryResolver.PER_PAGE[2]:
            limit = InventoryResolver.PER_PAGE[1]

        page = (page - 1) * limit

        if page > length:
            realpage = int(ceil(length / limit))
            page = limit * (realpage - 1)
            count = length - 1
        elif limit - 1 + page < length:
            count = limit - 1 + page
        else:
            count = length - 1

        return page, count + 1, realpage, count - page + 1
