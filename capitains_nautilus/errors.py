import MyCapytain.errors


class NautilusError(BaseException):
    """ An error has occurence"""
    CODE = None


class CTSError(NautilusError):
    CODE = None


class MissingParameter(CTSError):
    """ Request missing one or more required parameters """
    CODE = 1


class InvalidURNSyntax(CTSError):
    """ Invalid URN syntax """
    CODE = 2


class InvalidURN(CTSError, MyCapytain.errors.InvalidURN):
    """ Syntactically valid URN refers in invalid value  """
    CODE = 3


class InvalidLevel(CTSError):
    """ Invalid value for level parameter in GetValidReff request """
    CODE = 4


class InvalidContext(CTSError):
    """	Invalid value for context parameter in GetPassage or GetPassagePlus request """
    CODE = 5


class UnknownCollection(MyCapytain.errors.UnknownCollection, CTSError):
    """ Resource requested is not found """
    CODE = 6


class UndispatchedTextError(CTSError, MyCapytain.errors.UndispatchedTextError):
    """ A Text has not been dispatched """
    CODE = 7