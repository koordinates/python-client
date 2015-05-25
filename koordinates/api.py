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
import koordexceptions


class Connection(object):
    """
    This is a python library for accessing the koordinates api
    """

    def __init__(self, username, pwd=None, host='https://koordinates.com/'):
        self.username = username
        if pwd:
            self.pwd = pwd
        else:
            self.pwd = os.environ['KPWD']
        self.host = host
        self.layer = Layer(self)

    def get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)


class KoordinatesURLMixin(object):
    def __init__(self):
        self._url_templates = {}
        self._url_templates['GET'] = {}
        self._url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''
        self._url_templates['GET']['multi'] = '''https://koordinates.com/services/api/v1/layers/'''

    def url_templates(self, verb, urltype):
        return self._url_templates[verb][urltype]

    def get_url(self, verb, urltype, id=None):
        if id:
            return self.url_templates(verb, urltype).format(layer_id=id)
        else:
            return self.url_templates(verb, urltype)


class KoordinatesObjectMixin(object):

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

        self.attribute_sort_candidates = ['name']
        self.attribute_filter_candidates = ['name']

        super(self.__class__, self).__init__()

    def execute_get_list(self):

        target_url = self.url
        self.url = ""
        self.ordering_applied = False
        self.filtering_applied = False
        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code in [200, '200']:
            self.list_oflayer_dicts = self.raw_response.json()
        elif self.raw_response.status_code in [404, '404']:
            self.list_oflayer_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code in ['401', 401]:
            self.list_oflayer_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesNotAuthorised
        else:
            self.list_oflayer_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesUnexpectedServerResponse

        print("Finished in get_list")

    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('GET', 'multi', None)
        self.url = target_url
        return self

    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """
        from collections import namedtuple

        class StubClass(object):
            pass

        target_url = self.get_url('GET', 'single', id)
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
