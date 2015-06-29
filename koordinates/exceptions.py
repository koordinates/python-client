# -*- coding: utf-8 -*-
class KoordinatesException(Exception):
    pass


class KoordinatesValueException(KoordinatesException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidAPIVersion(KoordinatesException):
    pass

class InvalidURL(KoordinatesException):
    pass


class NotAuthorised(KoordinatesException):
    pass


class UnexpectedServerResponse(KoordinatesException):
    pass


class OnlyOneFilterAllowed(KoordinatesException):
    pass


class FilterMustNotBeSpaces(KoordinatesException):
    pass


class NotAValidBasisForFiltration(KoordinatesValueException):
    def __str__(self):
        return repr("Filter attribute :'{}' is not a valid basis for filtration")\
            .format(self.value)


class OnlyOneOrderingAllowed(KoordinatesValueException):
    pass


class NotAValidBasisForOrdering(KoordinatesValueException):
    def __str__(self):
        return repr("Sort attribute :'{}' is not a valid basis for sorting")\
            .format(self.value)

class AttributeNameIsReserved(KoordinatesException):
    pass

class ServerTimeOut(KoordinatesException):
    pass

class RateLimitExceeded(KoordinatesException):
    pass

class ImportEncounteredUpdateConflict(KoordinatesException):
    pass

class PublishAlreadyStarted(KoordinatesException):
    pass

class InvalidPublicationResourceList(KoordinatesException):
    pass
