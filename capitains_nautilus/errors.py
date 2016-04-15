# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class CTSError(BaseException):
    CODE = None


class MissingParameter(CTSError):
    """ Request missing one or more required parameters """
    CODE = 1


class InvalidURNSyntax(CTSError):
    """ Invalid URN syntax """
    CODE = 2


class InvalidURN(CTSError):
    """ Syntactically valid URN refers in invalid value  """
    CODE = 3


class InvalidLevel(CTSError):
    """ Invalid value for level parameter in GetValidReff request """
    CODE = 4


class InvalidContext(CTSError):
    """	Invalid value for context parameter in GetPassage or GetPassagePlus request """
    CODE = 5


class UnknownResource(CTSError):
    """ Resource requested is not found """
    CODE = 6
