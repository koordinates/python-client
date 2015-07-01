# -*- coding: utf-8 -*-

"""
koordinates.api
~~~~~~~~~~~~
This module implements the Koordinates API.

:copyright: (c) Koordinates .
:license: BSD, see LICENSE for more details.
"""

import logging
import os
import pprint
import uuid
from datetime import datetime
try:
    from urllib.parse import urlencode
    from urllib.parse import urlsplit
    from urllib.parse import parse_qs
except ImportError:
    from urllib import urlencode
    from urlparse import urlsplit
    from urlparse import parse_qs

import six
import requests

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
from .mixins import (
    KoordinatesURLMixin,
    KoordinatesObjectMixin
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
SUPPORTED_API_VERSIONS = ['v1', 'UNITTESTINGONLY']


logger = logging.getLogger(__name__)


class KData(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Data

    TODO: Description of what a `Data` is

    '''
    def __init__(self, parent, id=None):
        logger.info('Initializing KData object')
        self._parent = parent
        self._url = None
        self._id = id

        self._raw_response = None
        self._list_of_response_dicts = []
        self._link_to_next_in_list = ""
        self._next_page_number = 1
        self._attribute_sort_candidates = ['name']
        self._attribute_filter_candidates = ['name']
        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names
        self._attribute_reserved_names = []
        super(self.__class__, self).__init__()

    def get_list(self):
        """Fetches a set of sets
        """
        target_url = self.get_url('DATA', 'GET', 'multi')
        self._url = target_url
        return self

    def get(self, id):
        """Fetches a `KData` determined by the value of `id`.

        :param id: ID for the new :class:`KData` object.

        target_url = self.get_url('DATA', 'GET', 'single', {'data_id': id})
        super(self.__class__, self).get(id, target_url)
        """
        pass

