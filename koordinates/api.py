# -*- coding: utf-8 -*-

"""
koordinates.api
~~~~~~~~~~~~
This module implements the Koordinates API.

:copyright: (c) 2015 by Koordinates .
:license: BSD, see LICENSE for more details.
"""

import os
import requests
import json
from datetime import datetime
try:
        # from urllib.parse import urlparse
        from urllib.parse import urlencode
        from urllib.parse import urlsplit
        from urllib.parse import parse_qs
except ImportError:
        # from urlparse import urlparse
        from urllib import urlencode
        from urlparse import urlsplit
        from urlparse import parse_qs

import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path


import logging
logger = logging.getLogger(__name__)


import koordexceptions


class Connection(object):
    """
    This is a python library for accessing the koordinates api
    """

    def __init__(self, username, pwd=None, host='koordinates.com', activate_logging=True):
        if activate_logging:
            #d=datetime.now()
            client_logfile_name = "koordinates-client-{}.log".format(datetime.now().strftime('%Y%m%dT%H%M%S'))
            #client_logfile_name = "koordinates-client-{}.log".format(d=datetime.now().strftime('%Y%m%dT%H%M%S'))

            logging.basicConfig(filename=client_logfile_name,
                                level=logging.DEBUG, 
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('!!!! DONT FORGET LOGGING DEFAULTS TO TRUE. NEEDS CHANGING BEFORE 1.x.x  !!!!')
        logger.debug('Initializing Connection object')
        self.username = username
        if pwd:
            self.pwd = pwd
        else:
            self.pwd = os.environ['KPWD']
        self.host = host
        self.layer = Layer(self)
        self.set = Set(self)

    def get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)


class KoordinatesURLMixin(object):
    def __init__(self):
        self._url_templates = {}
        self._url_templates['LAYER'] = {}
        self._url_templates['LAYER'] ['GET'] = {}
        self._url_templates['LAYER'] ['GET']['single'] = '''https://{hostname}/services/api/v1/layers/{layer_id}/'''
        self._url_templates['LAYER'] ['GET']['multi'] = '''https://{hostname}/services/api/v1/layers/'''
        self._url_templates['SET'] = {}
        self._url_templates['SET'] ['GET'] = {}
        self._url_templates['SET'] ['GET']['single'] = '''https://{hostname}/services/api/v1/sets/{layer_id}/'''
        self._url_templates['SET'] ['GET']['multi'] = '''https://{hostname}/services/api/v1/sets/'''

    def url_templates(self, datatype, verb, urltype):
        return self._url_templates[datatype][verb][urltype]

    def get_url(self, datatype, verb, urltype, id=None):
        if id:
            return self.url_templates(datatype, verb, urltype)\
                    .format(hostname=self.parent.host, layer_id=id)
        else:
            return self.url_templates(datatype, verb, urltype)\
                    .format(hostname=self.parent.host)


class KoordinatesObjectMixin(object):

    def execute_get_list(self):
        import copy
        self.__execute_get_list_no_generator()
        for response in self.list_of_response_dicts:
            this_object = self.__class__(self.parent)
            for key, value in response.items():
                setattr(this_object, key, value)
            yield this_object


    def __execute_get_list_no_generator(self):

        target_url = self.url
        self.url = ""
        self.ordering_applied = False
        self.filtering_applied = False
        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code in [200, '200']:
            self.list_of_response_dicts = self.raw_response.json()
        elif self.raw_response.status_code in [404, '404']:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code in ['401', 401]:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesNotAuthorised
        else:
            self.list_oflayer_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesUnexpectedServerResponse

    def filter(self, value):
        if self.filtering_applied:
            raise koordexceptions.KoordinatesOnlyOneFilterAllowed

        # Eventually this check will be a good deal more sophisticated
        # so it's here in its current form to some degree as a placeholder
        if value.isspace():
            raise koordexceptions.KoordinatesFilterMustNotBeSpaces()

        self.add_query_component("q", value)
        self.filtering_applied = True
        return self

    def order_by(self, sort_key):
        if self.ordering_applied:
            raise koordexceptions.KoordinatesOnlyOneOrderingAllowed
        if sort_key not in self.attribute_sort_candidates:
            raise koordexceptions.KoordinatesNotAValidBasisForOrdering(sort_key)

        self.add_query_component("sort", sort_key)
        self.ordering_applied = True
        return self

    def add_query_component(self, argname, argvalue):

        # parse original string url
        url_data = urlsplit(self.url)

        # parse original query-string
        qs_data = parse_qs(url_data.query)

        # manipulate the query-string
        qs_data[argname] = [argvalue]

        # get the url with modified query-string
        self.url = url_data._replace(query=urlencode(qs_data, True)).geturl()


class Set(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Set  

    TODO: Description of what a `Set` is

    '''
    def __init__(self, parent, id=None):
        logger.info('Initializaing Set object')
        self.parent = parent
        self.url = None
        self._id = id
        self.list_of_response_dicts = []
        self.attribute_sort_candidates = ['name']
        self.attribute_filter_candidates = ['name']
        super(self.__class__, self).__init__()

    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('SET', 'GET', 'multi', None)
        self.url = target_url
        return self

    def get(self, id):
        """Fetches a Set determined by the value of `id`.

        :param id: ID for the new :class:`Set` object.
        """
        from collections import namedtuple

        class StubClass(object):
            pass

        target_url = self.get_url('SET', 'GET', 'single', id)
        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code == '200':
            layer_namedtuple = json.loads(self.raw_response.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            for k in layer_namedtuple.__dict__.keys():
                setattr(self, k, getattr(layer_namedtuple, k, ""))
        elif self.raw_response.status_code == '404':
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code == '401':
            raise koordexceptions.KoordinatesNotAuthorised
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse

class Layer(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items,
    but are manipulated as a single unit. Layers generally reflect collections
    of objects that you add on top of the map to designate a common
    association.
    '''
    def __init__(self, parent, id=None,
                 layer_name=None,
                 layer_type=None,
                 first_published_at=None,
                 published_at=None):

        self.parent = parent
        self.url = None
        self._id = id
        self.name = layer_name
        self._type = layer_type
        self._first_published_at = first_published_at
        self.cg_published_at = published_at
        self.ordering_applied = False
        self.filtering_applied = False

        self.raw_response = None
        self.list_of_response_dicts = []

        self.attribute_sort_candidates = ['name']
        self.attribute_filter_candidates = ['name']

        super(self.__class__, self).__init__()


    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('LAYER', 'GET', 'multi', None)
        self.url = target_url
        return self

    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """
        from collections import namedtuple

        class StubClass(object):
            pass

        target_url = self.get_url('LAYER', 'GET', 'single', id)
        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code == '200':
            layer_namedtuple = json.loads(self.raw_response.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            for k in layer_namedtuple.__dict__.keys():
                setattr(self, k, getattr(layer_namedtuple, k, ""))
        elif self.raw_response.status_code == '404':
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code == '401':
            raise koordexceptions.KoordinatesNotAuthorised
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse


def sample(foo, bar):
    """Is a Sample for testing purposes.
        :param foo: A sample integer
        :param bar: Another sample integer
    """

    return foo * bar
