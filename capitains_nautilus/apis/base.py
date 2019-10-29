from flask import request
from capitains_nautilus.errors import UnknownParameter
from capitains_nautilus.resolver_prototype import NautilusPrototypeResolver

def _none_or_string(var):
    if var is not None:
        return str(var)


def query_parameters_as_kwargs(params, mapping=None, typing=None):
    """ Default decorator to turn a dictionary of parameters into routes parameters
    """
    if not mapping:
        mapping = {}

    _typing = {k: _none_or_string for k in params}
    if typing:
        _typing.update(typing)

    def function_decorator(fn):
        def wrapper(*args):
            kwargs = {}
            for argument, default_value in params.items():
                kwargs[mapping.get(argument,  argument)] = \
                    _typing[argument](request.args.get(
                        argument,
                        default_value
                    ))
            return fn(*args, **kwargs)

        return wrapper
    return function_decorator


class AdditionalAPIPrototype:
    """ Additional APIs classes are used to connect new
    APIs to the Nautilus Flask Extensions

    :ivar nautilus_extension: Nautilus extension
    :type nautilus_extension: capitains_nautilus.flask_ext.FlaskNautilus
    """
    NAME = "Base"
    ROUTES = []
    Access_Control_Allow_Methods = {}
    CACHED = []

    def __init__(self):
        self.nautilus_extension = None

    def init_extension(self, nautilus_extension):
        self.nautilus_extension = nautilus_extension
        nautilus_extension.register(self, self.NAME)

    @property
    def resolver(self) -> NautilusPrototypeResolver:
        return self.nautilus_extension.resolver