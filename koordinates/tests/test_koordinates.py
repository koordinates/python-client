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
from __future__ import unicode_literals

import sys
import os
import unittest
import uuid

import responses
import requests
try:
        from urllib.parse import urlparse
        # from urllib.parse import urlencode
        # from urllib.parse import urlsplit
        # from urllib.parse import parse_qs
except ImportError:
        from urlparse import urlparse
        # from urllib import urlencode
        # from urlparse import urlsplit
        # from urlparse import parse_qs

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import api
import koordexceptions

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

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinates.pwd)
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = api.Connection('rshea@thecubagroup.com',
                                            invalid_password)

    def test_layers_url(self):
        self.assertTrue(self.koordconn.layer.get_url('GET', 'single', 999),
                        '''https://koordinates.com/services/api/v1/layers/999/''')

    def test_layers_url_template(self):
        self.assertTrue(self.koordconn.layer.url_templates('GET', 'single'),
                        '''https://koordinates.com/services/api/v1/layers/{layer_id}/''')

    @responses.activate
    def test_get_layerset_bad_auth_check_status(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.layer.get_url('GET', 'multi', id),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            self.bad_koordconn.layer.get_list().execute_get_list()
        except koordexceptions.KoordinatesNotAuthorised:
            pass

        self.assertTrue(self.bad_koordconn.layer.raw_response.status_code,
                        401)

    @responses.activate
    def test_get_layerset_bad_auth_check_exception(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.layer.get_url('GET', 'multi', id),
                      body=the_response, status=401,
                      content_type='application/json')

        with self.assertRaises(koordexceptions.KoordinatesNotAuthorised):
            self.bad_koordconn.layer.get_list().execute_get_list()

    @responses.activate
    def test_get_layerset(self):
        the_response = layers_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.layer.get_url('GET', 'multi', None),
                      body=the_response, status="200",
                      content_type='application/json')

        self.koordconn.layer.get_list().execute_get_list()

        self.assertEqual(len(self.koordconn.layer.list_oflayer_dicts), 100)

    @responses.activate
    def test_get_layerset_filter_and_sort(self):

        filter_value = str(uuid.uuid1())
        order_by_key = 'name'
        self.koordconn.layer.get_list().filter(filter_value).order_by(order_by_key)

        parsedurl = urlparse(self.koordconn.layer.url)

        self.assertTrue(self.contains_substring(parsedurl.query, filter_value))
        self.assertTrue(self.contains_substring(parsedurl.query, order_by_key))

    @responses.activate
    def test_get_layerset_bad_filter_and_sort(self):

        filter_value = str(uuid.uuid1())
        order_by_key = str(uuid.uuid1())

        with self.assertRaises(koordexceptions.KoordinatesNotAValidBasisForOrdering):
            self.koordconn.layer.get_list().filter(filter_value).order_by(order_by_key)

    @responses.activate
    def test_get_layer_by_id_bad_auth(self, id=1474):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.layer.get_url('GET', 'single', id),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            self.bad_koordconn.layer.get(id)
        except:
            pass

        self.assertEqual(self.bad_koordconn.layer.raw_response.status_code,
                         401)

    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = layers_single_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.layer.get_url('GET', 'single', id),
                      body=the_response, status="200",
                      content_type='application/json')

        self.koordconn.layer.get(id)

        self.assertEqual(self.koordconn.layer.name,
                         "Wellington City Building Footprints")
        self.assertEqual(self.koordconn.layer.raw_response.status_code,
                         "200")

    @responses.activate
    def test_use_of_responses(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                      body='{"error": "not found"}', status=404,
                      content_type='application/json')

        resp = requests.get('http://twitter.com/api/1/foobar')

        assert resp.json() == {"error": "not found"}

        self.assertEqual(len(responses.calls),  1)
        self.assertEqual(responses.calls[0].request.url,
                         'http://twitter.com/api/1/foobar')
        self.assertEqual(responses.calls[0].response.text,
                         '{"error": "not found"}')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
