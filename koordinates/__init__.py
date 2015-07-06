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
    ClientError,
    ClientValidationError,
    InvalidAPIVersion,
    ServerError,
    BadRequest,
    AuthenticationError,
    Forbidden,
    NotFound,
    NotAllowed,
    Conflict,
    RateLimitExceeded,
    InternalServerError,
    ServiceUnvailable,
)

from .client import Client
from .layers import Layer, Table
from .licenses import License
from .metadata import Metadata
from .publishing import Publish
from .publishrequest import PublishRequest
from .sets import Set
from .tokens import Token
from .users import Group, User

