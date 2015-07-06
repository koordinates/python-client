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

from .layer import (
    Version,
    Data,
    Datasource,
    Category,
    Autoupdate,
    License,
    Versioninstance,
    Field,
    Layer,
)

from .connection import Connection
from .metadata import Metadata
from .publish import Publish
from .publishrequest import PublishRequest
from .set import Set
from .tokens import Token
from .users import Group, User

