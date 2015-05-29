# -*- coding: utf-8 -*-
class KoordinatesBaseException(Exception):
    pass


class KoordinatesValueException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class KoordinatesInvalidAPIVersion(KoordinatesBaseException):
    pass

class KoordinatesInvalidURL(KoordinatesBaseException):
    pass


class KoordinatesNotAuthorised(KoordinatesBaseException):
    pass


class KoordinatesUnexpectedServerResponse(KoordinatesBaseException):
    pass


class KoordinatesOnlyOneFilterAllowed(KoordinatesBaseException):
    pass


class KoordinatesFilterMustNotBeSpaces(KoordinatesBaseException):
    pass


class KoordinatesNotAValidBasisForFiltration(KoordinatesValueException):
    def __str__(self):
        return repr("Filter attribute :'{}' is not a valid basis for filtration")\
            .format(self.value)


class KoordinatesOnlyOneOrderingAllowed(KoordinatesValueException):
    pass


class KoordinatesNotAValidBasisForOrdering(KoordinatesValueException):
    def __str__(self):
        return repr("Sort attribute :'{}' is not a valid basis for sorting")\
            .format(self.value)

class KoordinatesAttributeNameIsReserved(KoordinatesBaseException):
    pass

class KoordinatesServerTimeOut(KoordinatesBaseException):
    pass

class KoordinatesRateLimitExceeded(KoordinatesBaseException):
    pass
