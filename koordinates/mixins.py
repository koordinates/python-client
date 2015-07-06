# -*- coding: utf-8 -*-

"""
koordinates.mixins
~~~~~~~~~~~~~~

This module provides mixin classes used in the Koordinates
Client Library

"""
import abc
import logging
import pprint
import json

import requests
import dateutil.parser
from six.moves import urllib

from .utils import (
    dump_class_attributes_to_dict,
    remove_empty_from_dict,
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

logger = logging.getLogger(__name__)

class KoordinatesURLMixin(object):
    '''
    A Mixin to support URL operations
    '''
    URL_TEMPLATES = {
        'CLIENT': {
            'POST': {
                'publishmulti': '/publish/',
            },
        },
        'LAYER': {
            'GET': {
                'singleversion': '/layers/{layer_id}/versions/{version_id}/',
                'single': '/layers/{id}/',
                'multi': '/layers/',
                'multidraft': '/layers/drafts/',
            },
            'POST': {
                'create': '/layers/',
                'update': '/layers/{layer_id}/import/',
            },
        },
        'SET': {
            'GET': {
                'single': '/sets/{id}/',
                'multi': '/sets/',
            },
        },
        'VERSION': {
            'GET': {
                'single': '/layers/{layer_id}/versions/{version_id}/',
                'multi': '/layers/{layer_id}/versions/',
                'draft': '/layers/{layer_id}/versions/draft/',
                'published': '/layers/{layer_id}/versions/published/',
            },
            'POST': {
                'create': '/layers/{layer_id}/versions/',
                'import': '/layers/{layer_id}/versions/{version_id}/import/',
                'publish': '/layers/{layer_id}/versions/{version_id}/publish/',
            },
            'PUT': {
                'update': '/layers/{layer_id}/versions/{version_id}/',
            }
        },
        'DATA': {
            'GET': {
                'multi': '/data/',
            },
        },
        'TABLE': {
            'GET': {
                'singleversion': '/tables/{table_id}/versions/{version_id}/',
            },
        },
        'PUBLISH': {
            'GET': {
                'single': '/publish/{id}/',
                'multi': '/publish/',
            },
            'DELETE': {
                'single': '/publish/{id}/',
            }
        },
        'TOKEN': {
            'GET': {
                'single': '/tokens/{id}/',
                'multi': '/tokens/',
            },
            'POST': {
                'create': '/tokens/',
            },
            'PUT': {
                'update': '/tokens/{id}/',
            },
            'DELETE': {
                'single': '/tokens/{id}/',
            },
        },
        'LICENSE': {
            'GET': {
                'single': '/licenses/{id}/',
                'multi': '/licenses/',
                'cc': '/licenses/{slug}/{jurisdiction}/',
            },
        },
    }

    def get_url(self, datatype, verb, urltype, optargs=None ):
        """Returns a fully formed url

        :param datatype: a string identifying the data the url will access .
        :param verb: the HTTP verb needed for use with the url .
        :param urltype: an adjective used to the nature of the request .
        :param \*\*optargs: Optional arguments that allows override of the hostname or api version to be embedded in teh resulting url.
        :return: string
        :rtype: A fully formed url.
        """
        if optargs is None:
            optargs = {}

        if "hostname" not in optargs:
            try:
                optargs['hostname'] = self._parent.host
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Client`
                # object itself
                optargs['hostname'] = self.host
        if "api_version" not in optargs:
            try:
                optargs['api_version'] = self._parent.api_version
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Client`
                # object itself
                optargs['api_version'] = self.api_version

        url = "https://{hostname}/services/api/{api_version}"
        url += self.URL_TEMPLATES[datatype][verb][urltype]
        return url.format(**optargs)
