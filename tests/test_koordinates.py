#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_koordinates
----------------------------------

Tests for `koordinates` module.

:copyright: (c) 2015 by Koordinates .
:license: BSD, see LICENSE for more details.
"
"""
#from __future__ import unicode_literals
#from __future__ import absolute_import

import sys
import os
import unittest
import uuid

import responses
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import koordinates

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from canned_responses_for_tests import layers_multiple_good_simulated_response
from canned_responses_for_tests import layers_single_good_simulated_response

def getpass():
    '''
    Prompt user for Password until there is a Connection object
    '''
    import getpass
    if ('CIRCLECI' in os.environ) and ('KPWD' in os.environ):
        return os.environ['KPWD']
    else:
        return(getpass.getpass('Please enter your Koordinates password: '))


class TestKoordinates(unittest.TestCase):

    pwd = getpass()


    def setUp(self):
        self.koordconn = koordinates.api.Connection('rshea@thecubagroup.com', TestKoordinates.pwd)
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = koordinates.api.Connection('rshea@thecubagroup.com', invalid_password)

    def test_layers_url_template(self):
        self.koordconn.layer(999)

        assert self.koordconn.layer.url('GET', 'single') == '''https://koordinates.com/services/api/v1/layers/999/'''


    def test_layers_url_template(self):
        assert self.koordconn.layer.url_templates('GET', 'single') == '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''

    @responses.activate
    def test_get_layerset_bad_auth(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET, self.bad_koordconn.layer.url('GET', 'multi', id),  
                      body=the_response, status=401,
                      content_type='application/json')

        self.bad_koordconn.layer.list(id)
        
        assert self.bad_koordconn.layer.raw_response.status_code == 401 

    @responses.activate
    def test_get_layerset(self):
        the_response = layers_multiple_good_simulated_response

        responses.add(responses.GET, self.koordconn.layer.url('GET', 'multi', None),  
                      body=the_response, status="200",
                      content_type='application/json')

        self.koordconn.layer.list()

        assert len(self.koordconn.layer.list_oflayer_dicts) == 100
        

    @responses.activate
    def test_get_layer_by_id_bad_auth(self, id=1474):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET, self.bad_koordconn.layer.url('GET', 'single', id),  
                      body=the_response, status=401,
                      content_type='application/json')

        self.bad_koordconn.layer.get(id)
        
        assert self.bad_koordconn.layer.raw_response.status_code == 401 

    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = layers_single_good_simulated_response

        responses.add(responses.GET, self.koordconn.layer.url('GET', 'single', id),  
                      body=the_response, status="200",
                      content_type='application/json')

        self.koordconn.layer.get(id)
        
        assert self.koordconn.layer.name == "Wellington City Building Footprints" 
        assert self.koordconn.layer.raw_response.status_code == "200" 

    @responses.activate
    def test_use_of_responses(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                    body='{"error": "not found"}', status=404,
                    content_type='application/json')
 
        resp = requests.get('http://twitter.com/api/1/foobar')
 
        assert resp.json() == {"error": "not found"}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://twitter.com/api/1/foobar'
        assert responses.calls[0].response.text == '{"error": "not found"}'
 
    @responses.activate
    def test_basic_auth_1(self):
        the_url = '''http://httpbin.org/basic-auth/user/passwd'''
        the_response = '''
            {
              "authenticated": true, 
              "user": "user"
            }
        '''
        import json
        the_response = json.dumps({'authenticated':True, 'user':'user'})
        the_response.replace('\'' , '"')

        responses.add(responses.GET, the_url,  
                      body=the_response, status=200,
                      content_type='application/json')

        resp = requests.get(the_url)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == the_url 
        assert responses.calls[0].response.text == the_response

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
