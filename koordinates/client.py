# -*- coding: utf-8 -*-

"""
koordinates.client
==================
"""

import logging
import copy
import os
import sys

import requests

from . import layers, licenses, publishing, sets, tokens, users, catalog
from . import exceptions


logger = logging.getLogger(__name__)


class Client(object):
    """
    A `Client` is used to define the host and api-version which the user
    wants to connect to. The user identity is also defined when `Client`
    is instantiated.
    """
    def __init__(self, host, token=None, activate_logging=False):
        '''
        :param str host: the domain name of the Koordinates site to connect to (eg. ``labs.koordinates.com``)
        :param str token: Koordinates API token to use for authentication
        :param bool activate_logging: if True then logging to stderr is activated
        '''
        if activate_logging:
            logging.basicConfig(stream=sys.stderr,
                                level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('Initializing Client object for %s', host)

        self.host = host

        if token:
            self.token = token
        elif 'KOORDINATES_TOKEN' in os.environ:
            self.token = os.environ['KOORDINATES_TOKEN']
        else:
            raise KeyError('No authentication token specified, and KOORDINATES_TOKEN not available in the environment.')

        self._init_managers(public={
                'sets': sets.SetManager,
                'publishing': publishing.PublishManager,
                'tokens': tokens.TokenManager,
                'layers': layers.LayerManager,
                'tables': layers.TableManager,
                'licenses': licenses.LicenseManager,
                'catalog': catalog.CatalogManager,
            },
            private=(
                users.GroupManager,
                users.UserManager,
            )
        )

        super(self.__class__, self).__init__()

    def _init_managers(self, public, private):
        self._manager_map = {}
        for alias, manager_class in public.items():
            mgr = manager_class(self)
            self._manager_map[mgr.model] = mgr
            setattr(self, alias, mgr)

        for manager_class in private:
            mgr = manager_class(self)
            self._manager_map[mgr.model] = mgr

    def get_manager(self, model):
        """
        Return the active manager for the given model.
        :param model: Model class to look up the manager instance for.
        :return: Manager instance for the model associated with this client.
        """
        return self._manager_map[model]

    def _assemble_headers(self, method, user_headers=None):
        """
        Takes the supplied headers and adds in any which
        are defined at a client level and then returns
        the result.

        :param user_headers: a `dict` containing headers defined at the
                             request level, optional.

        :return: a `dict` instance
        """

        headers = copy.deepcopy(user_headers or {})

        if self.token:
            headers['Authorization'] = 'key {token}'.format(token=self.token)

        headers.setdefault('Accept', 'application/json')

        if method not in ('GET', 'HEAD'):
            headers.setdefault('Content-type', 'application/json')

        return headers

    def request(self, method, url, *args, **kwargs):
        headers = self._assemble_headers(method, kwargs.pop("headers", {}))
        r = self._raw_request(method, url, headers, *args, **kwargs)

        if method == 'POST':
            # If we're posting to an endpoint
            if r.status_code in (requests.codes.created, requests.codes.accepted):
                # and we get a 201/202 response
                if 'location' in r.headers:
                    # with a location header
                    logger.info("%s -> %s", r.status_code, r.headers['location'])

                    # follow it and return the results of the GET
                    r2 = self.request('GET', r.headers['location'])
                    r2.parent_response = r
                    return r2

        return r

    def _raw_request(self, method, url, headers, *args, **kwargs):
        logger.info('Request: %s %s %s', method, url, headers)
        try:
            r = requests.request(method,
                                 url,
                                 headers=headers,
                                 *args,
                                 **kwargs)
            logger.info('Response: %d %s in %s', r.status_code, r.reason, r.elapsed)
            logger.debug('Response: headers=%s', r.headers)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            logger.warn('Response: %s: %s', e, r.text)
            raise exceptions.ServerError.from_requests_error(e)
        except requests.RequestException as e:
            raise exceptions.ServerError.from_requests_error(e)

    def get_url_path(self, datatype, verb, urltype, params={}, api_version=None):
        api_version = api_version or 'v1'
        templates = getattr(self, 'URL_TEMPLATES__%s' % api_version)

        url = templates[datatype][verb][urltype]
        return url.format(**params)

    def get_url(self, datatype, verb, urltype, params={}, api_host=None, api_version=None):
        """Returns a fully formed url

        :param datatype: a string identifying the data the url will access.
        :param verb: the HTTP verb needed for use with the url.
        :param urltype: an adjective used to the nature of the request.
        :param \*\*params: substitution variables for the URL.
        :return: string
        :rtype: A fully formed url.
        """
        api_version = api_version or 'v1'
        api_host = api_host or self.host

        subst = params.copy()
        subst['api_host'] = api_host
        subst['api_version'] = api_version

        url = "https://{api_host}/services/api/{api_version}"
        url += self.get_url_path(datatype, verb, urltype, params, api_version)
        return url.format(**subst)

    URL_TEMPLATES__v1 = {
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
            'DELETE': {
                'delete': '/layers/{id}/',
            }
        },
        'SET': {
            'GET': {
                'single': '/sets/{id}/',
                'metadata': '/sets/{id}/metadata',
                'multi': '/sets/',
            },
            'POST': {
                'create': '/sets/',
            },
            'PUT': {
                'update': '/sets/{id}/',
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
                'edit': '/layers/{layer_id}/versions/{version_id}/',
            }
        },
        'CATALOG': {
            'GET': {
                'multi': '/data/',
                'latest': '/data/latest/',
            },
        },
        'PUBLISH': {
            'GET': {
                'single': '/publish/{id}/',
                'multi': '/publish/',
            },
            'POST': {
                'create': '/publish/',
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
        'METADATA': {
            # InnerManager, so relative to a parent object
            'POST': {
                'set': 'metadata/',
            }
        }
    }
