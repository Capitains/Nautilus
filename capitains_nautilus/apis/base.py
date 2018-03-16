from abc import abstractmethod
from flask import current_app


class AdditionalAPIPrototype:
    """ Additional APIs classes are used to connect new
    APIs to the Nautilus Flask Extensions

    :param nautilus_extension: Nautilus extension
    """
    ROUTES = []
    Access_Control_Allow_Methods = {}
    CACHED = []

    def __init__(self, nautilus_extension):
        self.nautilus_extension = nautilus_extension

    @property
    def resolver(self):
        return self.nautilus_extension.resolver