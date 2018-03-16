class AdditionalAPIPrototype:
    """ Additional APIs classes are used to connect new
    APIs to the Nautilus Flask Extensions

    :ivar nautilus_extension: Nautilus extension
    :type nautilus_extension: capitains_nautilus.flask_ext.FlaskNautilus
    """
    ROUTES = []
    Access_Control_Allow_Methods = {}
    CACHED = []

    def init_extension(self, nautilus_extension):
        self.nautilus_extension = nautilus_extension

    @property
    def resolver(self):
        return self.nautilus_extension.resolver