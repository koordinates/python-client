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

class Layer(object):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items, 
    but are manipulated as a single unit. Layers generally reflect collections 
    of objects that you add on top of the map to designate a common association.
    '''
    def __init__(self, username, pwd=None, id=None, 
                layer_name=None, 
                layer_type=None, 
                first_published_at=None, 
                published_at=None):

        self._username = username
        #import pdb;pdb.set_trace()
        if pwd:
            self._pwd = pwd
        else:
            self._pwd = os.environ['KPWD']

        self._id = id
        self.name = layer_name
        self._type = layer_type
        self._first_published_at = first_published_at
        self.cg_published_at = published_at

        self._url_templates = {}
        self._url_templates['GET'] = {}
        self._url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''


    def __get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self._username, self._pwd)

    def url_templates(self, verb, urltype):
        return self._url_templates[verb][urltype]

    def url(self, verb, urltype, id):
        return self.url_templates(verb, urltype).format(layer_id=id)


    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """
        import json
        from requests.auth import HTTPBasicAuth

        target_url = self.url('GET', 'single', id)
        req_resp = requests.get(target_url, auth=self.__get_auth())
        layer_dict =  req_resp.json()

        self.name = layer_dict['name']
        self._type = layer_dict['type']
        self._type = layer_dict['type']
        self._first_published_at = layer_dict['first_published_at']



    def list(self, filters):
        pass
    

def sample(foo, bar):
    """Is a Sample for testing purposes.

    :param foo: A sample integer
    :param bar: Another sample integer

    """

    return foo * bar
