#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_publish    
----------------------------------

Tests for the publishing part of the
`koordinates` module.

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
except ImportError:
        from urlparse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import api
import koordexceptions

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from canned_responses_for_tests_1 import layers_multiple_good_simulated_response
from canned_responses_for_tests_2 import layers_single_good_simulated_response
from canned_responses_for_tests_3 import sets_single_good_simulated_response
from canned_responses_for_tests_4 import sets_multiple_good_simulated_response
from canned_responses_for_tests_5 import layers_version_single_good_simulated_response
from canned_responses_for_tests_6 import layers_version_multiple_good_simulated_response
from canned_responses_for_tests_7 import publish_single_good_simulated_response
from canned_responses_for_tests_7 import publish_multiple_get_simulated_response

from . import package_pwd

class TestKoordinatesPublishing(unittest.TestCase):

    pwd = package_pwd

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinatesPublishing.pwd)
        self.koordtestconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinatesPublishing.pwd, 
                                        host="test.koordinates.com")
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = api.Connection('rshea@thecubagroup.com',
                                            invalid_password)

    @responses.activate
    def test_publish_get_by_id(self):
        the_response = publish_single_good_simulated_response

        publish_id = 2054 
        responses.add(responses.GET,
                      self.koordconn.publish.get_url('PUBLISH', 'GET', 'single', {'publish_id': publish_id}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.publish.get(publish_id)

    @responses.activate
    def test_multipublish_resource_specification(self):
        the_response = '''{}''' 
        responses.add(responses.POST,
                      self.koordtestconn.get_url('CONN', 'POST', 'publishmulti', kwargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("")

        pr = api.PublishRequest(kwargs={'hostname':"test.koordinates.com"})
        pr.add_layer_to_publish(100, 1000)
        pr.add_layer_to_publish(101, 1001)
        pr.add_layer_to_publish(102, 1002)
        pr.add_table_to_publish(200, 2000)
        pr.add_table_to_publish(201, 2001)
        pr.add_table_to_publish(202, 2002)

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr)

    @responses.activate
    def test_multipublish_bad_args(self):
        the_response = '''{}''' 

        responses.add(responses.POST,
                      self.koordtestconn.layer.get_url('CONN', 'POST', 'publishmulti', kwargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("")

        pr = api.PublishRequest([],[])

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr)

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("", 'Z')

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish(pr, 'Z')

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr, 'together')

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish(pr, 'together', 'Z')

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr, 'together', 'abort')

    @responses.activate
    def test_publish_single_layer_version(self, layer_id=1474, version_id=4067):
        the_response = layers_version_single_good_simulated_response 
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id}),
                      body=the_response, status=200,
                      content_type='application/json')



        #import pdb;pdb.set_trace()
        self.koordconn.version.get(1474, 4067)

        self.assertEqual(self.koordconn.version.id, 1474)
        self.assertEqual(self.koordconn.version.version.id, 4067)
    
        the_response = '''{"id": 2057, "url": "https://test.koordinates.com/services/api/v1/publish/2057/", "state": "publishing", "created_at": "2015-06-08T10:39:44.823Z", "created_by": {"id": 18504, "url": "https://test.koordinates.com/services/api/v1/users/18504/", "first_name": "Richard", "last_name": "Shea", "country": "NZ"}, "error_strategy": "abort", "publish_strategy": "together", "publish_at": null, "items": ["https://test.koordinates.com/services/api/v1/layers/1474/versions/4067/"]}'''

        responses.add(responses.POST,
                      self.koordconn.get_url('VERSION', 'POST', 'publish', {'layer_id': layer_id, 'version_id': version_id}),
                      body=the_response, status=201,
                      content_type='application/json')

        self.koordconn.version.publish()
        self.assertTrue(self.contains_substring(self.koordconn.version._raw_response.text , "created_by"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
