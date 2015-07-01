# -*- coding: utf-8 -*-
'''
Koordinates API Library

:copyright: (c) Koordinates .
:license: BSD, see LICENSE for more details.

'''

__title__ = 'koordinates'
__version__ = '0.0.1'
__author__ = 'Richard Shea'
__license__ = 'BSD'
__copyright__ = 'Copyright Koordinates Limited'


import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


from .utils import (
    remove_empty_from_dict,
    dump_class_attributes_to_dict,
    make_date_list_from_string_list,
    make_date,
    make_date_if_possible,
    make_list_of_Datasources,
    make_list_of_Fields,
    make_list_of_Categories
)

from .api import Layer
from .connection import Connection


from .exceptions import (
    KoordinatesException,
    KoordinatesValueException,
    InvalidAPIVersion,
    InvalidURL,
    NotAuthorised,
    UnexpectedServerResponse,
    OnlyOneFilterAllowed,
    FilterMustNotBeSpaces,
    NotAValidBasisForFiltration,
    OnlyOneOrderingAllowed,
    NotAValidBasisForOrdering,
    AttributeNameIsReserved,
    ServerTimeOut,
    RateLimitExceeded,
    ImportEncounteredUpdateConflict,
    PublishAlreadyStarted,
    InvalidPublicationResourceList
)
