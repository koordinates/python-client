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

from .mixins import KoordinatesURLMixin
from . import layers, licenses, metadata, publishing, sets, tokens, users
from .publishrequest import PublishRequest
from . import exceptions


logger = logging.getLogger(__name__)


SUPPORTED_API_VERSIONS = ['v1', 'UNITTESTINGONLY']


class Client(KoordinatesURLMixin):
    """
    A `Client` is used to define the host and api-version which the user
    wants to connect to. The user identity is also defined when `Client`
    is instantiated.
    """
    def __init__(self, host, token=None,
                 api_version='v1', activate_logging=False):
        '''
        :param str host: the domain name of the Koordinates site to connect to (eg. ``labs.koordinates.com``)
        :param str token: Koordinates API token to use for authentication
        :param str api_version: the version of the api to connect to
        :param bool activate_logging: if True then logging to stderr is activated
        '''
        if activate_logging:
            logging.basicConfig(stream=sys.stderr,
                                level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('Initializing Client object for %s', host)

        if api_version not in SUPPORTED_API_VERSIONS:
            raise exceptions.InvalidAPIVersion(api_version)
        else:
            self.api_version = api_version

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
            },
            private=(
                users.GroupManager,
                users.UserManager,
                metadata.MetadataManager,
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

    def assemble_headers(self, method, user_headers=None):
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

    def build_multi_publish_json(self, pub_request, publish_strategy, error_strategy):
        '''
        Build a JSON body suitable for the multi-resource
        publishing

        :param pub_request: a PublishRequest instance .
        :param pub_strategy: a string defining the publish_strategy.
        :param error_strategy: a string defining the error_strategy.

        :return: a dictionary which corresponds to the body required\
                when doing a `Client.multipublish` of resources.

        '''

        pub_request.validate()

        dic_out = {}
        if publish_strategy:
            dic_out['publish_strategy'] = publish_strategy
        if error_strategy:
            dic_out['error_strategy'] = error_strategy

        lst_items = []

        for table_resource_dict in pub_request.tables:
            table_resource_dict['hostname'] = self.host
            table_resource_dict['api_version'] = self.api_version
            target_url = self.get_url('TABLE', 'GET', 'singleversion', table_resource_dict)
            lst_items.append(target_url)

        for layer_resource_dict in pub_request.layers:
            layer_resource_dict['hostname'] = self.host
            layer_resource_dict['api_version'] = self.api_version
            target_url = self.get_url('LAYER', 'GET', 'singleversion', layer_resource_dict)
            lst_items.append(target_url)

        dic_out['items'] = lst_items

        return dic_out

    def request(self, method, url, *args, **kwargs):
        headers = self.assemble_headers(method, kwargs.pop("headers", {}))
        return self._raw_request(method, url, headers, *args, **kwargs)

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

    def multi_publish(self, pub_request, publish_strategy=None, error_strategy=None):
        """
        Publishes a set of items, potentially a mixture of Layers and Tables

        :param pub_request: A `PublishRequest' object specifying what resources are to be published
        :param pub_strategy: A string defining the publish_strategy. One of: `"individual"`, `"together"`. Default = `"together"`
        :param error_strategy: a string defining the error_strategy. One of: `"abort"`, `"ignore"`. Default = `"abort"`

        :return: a dictionary which corresponds to the body required\
                when doing a `Client.multipublish` of resources.

        """

        assert type(pub_request) is PublishRequest,\
            "The 'pub_request' argument must be a PublishRequest instance"
        assert publish_strategy in ["individual", "together", None],\
            "The 'publish_strategy' value must be None or 'individual' or 'together'"
        assert error_strategy in ["abort", "ignore", None],\
            "The 'error_strategy' value must be None or 'abort' or 'ignore'"

        dic_args = {}
        if pub_request.hostname:
            dic_args = {'hostname': pub_request.hostname}
        if pub_request.api_version:
            dic_args = {'api_version': pub_request.api_version}

        target_url = self.get_url('CLIENT', 'POST', 'publishmulti', dic_args)
        dic_body = self.build_multi_publish_json(pub_request, publish_strategy, error_strategy)
        r = self.request('POST', target_url, json=dic_body)
        return r