from flask import request


def query_parameters_as_kwargs(params, mapping=None):
    """ Default decorator to turn a dictionary of parameters into routes parameters
    """
    if not mapping:
        mapping = {}

    def function_decorator(function):
        def wrapper(*args):
            kwargs = {}
            for argument, default_value in params.items():

                kwargs[mapping.get(argument,  argument)] = \
                    request.args.get(argument, default_value)

            return function(*args, **kwargs)

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
    def resolver(self):
        return self.nautilus_extension.resolver