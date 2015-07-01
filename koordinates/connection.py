# -*- coding: utf-8 -*-

"""
koordinates.connection
~~~~~~~~~~~~
This module implements the Connection class for the Koordinates
Client Library.

:copyright: (c) Koordinates .
:license: BSD, see LICENSE for more details.
"""

import logging
import os
from datetime import datetime

import requests

from .mixins import KoordinatesURLMixin
from .layer import Layer, Version
from .publish import Publish, PublishRequest
from .set import Set
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

SUPPORTED_API_VERSIONS = ['v1', 'UNITTESTINGONLY']

class Connection(KoordinatesURLMixin):
    """
    A `Connection` is used to define the host and api-version which the user
    wants to connect to. The user identity is also defined when `Connection`
    is instantiated.
    """

    def __init__(self, username, pwd=None, host='koordinates.com',
                 api_version='v1', activate_logging=True):
        '''
        :param username: the username under which to make the connections
        :param pwd: the password under which to make the connections
        :param host: the host to connect to
        :param api_version: the version of teh api to connect to
        :param activate_logging: When True then logging to timestamped log files is activated

        '''
        if activate_logging:
            client_logfile_name = "koordinates-client-{}.log"\
                                  .format(datetime.now().strftime('%Y%m%dT%H%M%S'))
            logging.basicConfig(filename=client_logfile_name,
                                level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('Initializing Connection object')

        if api_version not in SUPPORTED_API_VERSIONS:
            #raise InvalidAPIVersion
            raise InvalidAPIVersion
        else:
            self.api_version = api_version

        self.host = host

        self.username = username
        if pwd:
            self.pwd = pwd
        else:
            self.pwd = os.environ['KPWD']

        self.sets = Set._meta.manager
        self.sets.set_connection(self)

        self.layer = Layer(self)
        self.version = Version(self)
        from .api import KData
        self.data = KData(self)
        self.publish = Publish(self)

        super(self.__class__, self).__init__()

    def get_auth(self):
        """Creates an Authorisation object based on the
        instance data of the `Connection` instance.


        :return: a `requests.auth.HTTPBasicAuth` instance
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)

    def build_multi_publish_json(self, pub_request, publish_strategy, error_strategy):
        '''
        Build a JSON body suitable for the multi-resource
        publishing

        :param pub_request: a PublishRequest instance .
        :param pub_strategy: a string defining the publish_strategy.
        :param error_strategy: a string defining the error_strategy.

        :return: a dictionary which corresponds to the body required\
                when doing a `Connection.multipublish` of resources.

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
        # headers = {
        #     'Content-type': 'application/json',
        #     'Accept': '*/*',
        # }
        r = requests.request(method, url, auth=self.get_auth(), *args, **kwargs)
        return r

    def multi_publish(self, pub_request, publish_strategy=None, error_strategy=None):
        """Publishes a set of items, potentially a mixture of Layers and Tables

        :param pub_request: A `PublishRequest' object specifying what resources are to be published
        :param pub_strategy: A string defining the publish_strategy. One of: `"individual"`, `"together"`. Default = `"together"`
        :param error_strategy: a string defining the error_strategy. One of: `"abort"`, `"ignore"`. Default = `"abort"`

        :return: a dictionary which corresponds to the body required\
                when doing a `Connection.multipublish` of resources.

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

        target_url = self.get_url('CONN', 'POST', 'publishmulti', dic_args)
        dic_body = self.build_multi_publish_json(pub_request, publish_strategy, error_strategy)
        r = self.request('POST', target_url, json=dic_body)

        if r.status_code == 201:
            # Success !
            pass
        elif r.status_code == 404:
            # The resource specificed in the URL could not be found
            raise InvalidURL
        elif r.status_code == 409:
            # Indicates that the request could not be processed because
            # of conflict in the request, such as an edit conflict in
            # the case of multiple updates
            raise ImportEncounteredUpdateConflict
        else:
            raise UnexpectedServerResponse


