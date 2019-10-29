import MyCapytain.errors

# next level over-engineering thanks to stackoverflow


class NautilusError(BaseException):
    """ An error has occurred"""
    CODE = None
    NAME = "UnknownError"

    def __repr__(self):
        return "<{} ({})>".format(type(self), self.title)

    def __init__(self, description=None):
        self.title = self.NAME
        self.description = description or self.__doc__


class CTSError(NautilusError):
    """ Unknown error """
    CODE = None
    NAME = "CTSUnknownError"


class CtsMissingParameter(CTSError):
    """ Request missing one or more required parameters """
    NAME = "MissingParameter"
    CODE = 1


class CtsInvalidURNSyntax(CTSError):
    """ Invalid URN syntax """
    CODE = 2
    NAME = "InvalidURNSyntax"


class CtsInvalidURN(CTSError, MyCapytain.errors.InvalidURN):
    """ Syntactically valid URN refers to an invalid level of collection for this request"""
    CODE = 3
    NAME = "InvalidURN"


class CtsInvalidLevel(CTSError):
    """ Invalid value for level parameter in GetValidReff request """
    CODE = 4
    NAME = "InvalidLevel"


class CtsInvalidContext(CTSError):
    """ Invalid value for context parameter in GetPassage or GetPassagePlus request """
    CODE = 5
    NAME = "InvalidContext"


class CtsUnknownCollection(CTSError, MyCapytain.errors.UnknownCollection):
    """ Resource requested is not found """
    CODE = 6
    NAME = "UnknownCollection"


class CtsUndispatchedTextError(CTSError, MyCapytain.errors.UndispatchedTextError):
    """ A Text has not been dispatched """
    CODE = 7
    NAME = "UndispatchedTextError"


class CtsUnknownParameter(NautilusError):
    """ A parameter is unknown to the API """
    NAME = "UnknownParameter"


class UnknownParameter(NautilusError):
    """ A parameter is unknown to the API """


class MissingParameter(NautilusError):
    """ A parameter is unknown to the API """
