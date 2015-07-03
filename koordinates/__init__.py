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
    Group,
    Data,
    Datasource,
    Category,
    Autoupdate,
    Createdby,
    License,
    Versioninstance,
    Metadata,
    Field,
    Layer,
)

from .publish import (
    PublishRequest,
    Publish,
)
from .set import Set
from .connection import Connection

