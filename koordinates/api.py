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


class Layer(object):
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
        self._id = id
        self.name = layer_name
        self._type = layer_type
        self._first_published_at = first_published_at
        self.cg_published_at = published_at

        self._url_templates = {}
        self._url_templates['GET'] = {}
        self._url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''
        self._url_templates['GET']['multi'] = '''https://koordinates.com/services/api/v1/layers/'''
        self.raw_response = None

    def url_templates(self, verb, urltype):
        return self._url_templates[verb][urltype]

    def url(self, verb, urltype, id=None):
        if id:
            return self.url_templates(verb, urltype).format(layer_id=id)
        else:
            return self.url_templates(verb, urltype)

    def list(self, filters=None):
        """Fetches a set of layers
        """
        target_url = self.url('GET', 'multi', None)
        self.raw_response = requests.get(target_url, auth=self.parent.get_auth())

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

    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """
        from collections import namedtuple

        class StubClass(object):
            pass

        target_url = self.url('GET', 'single', id)
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
