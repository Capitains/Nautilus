class cached_property:
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    and https://github.com/pydanny/cached-property/blob/master/cached_property.py
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__", None)
        self.func = func
        self.setter_func = None

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def __set__(self, obj, value):
        del obj.__dict__[self.func.__name__]
        self.setter_func(obj, value)

    def setter(self, decorated_funtion):
        self.setter_func = decorated_funtion
        return self.__set__


class Store:
    IGNORE = False
    def __init__(self):
        self.objects = {}

    def __contains__(self, item):
        if item in self.objects:
            return True

    def __getitem__(self, item):
        return self.objects[item]

    def connect(self, func):
        def get_item(obj, item):
            if not self.IGNORE and item in self:
                return self.objects[item]
            return func(obj, item)
        return get_item


STORE = Store()
