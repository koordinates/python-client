# -*- coding: utf-8 -*-
'''
Koordinates Python API Client Library

:copyright: (c) Koordinates Limited.
:license: BSD, see LICENSE for more details.
'''

__version__ = '0.4.1'

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
from .sets import Set
from .sources import Source, UploadSource
from .tokens import Token
from .users import Group, User
from .permissions import Permission
from .exports import Export, CropLayer, DownloadError
