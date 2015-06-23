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
except ImportError:
        from urlparse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import api
import koordexceptions

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from canned_responses_for_tests_1 import layers_multiple_good_simulated_response
from canned_responses_for_tests_2 import layers_single_good_simulated_response


from . import package_pwd

class TestKoordinatesURLHandling(unittest.TestCase):

    pwd = package_pwd

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinatesURLHandling.pwd)
        self.koordtestconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinatesURLHandling.pwd, 
                                        host="test.koordinates.com")
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = api.Connection('rshea@thecubagroup.com',
                                            invalid_password)

    @responses.activate
    def test_layer_hierarchy_of_classes(self):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id': 1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.layer.get(1474, dynamic_build = False)
        self.assertEqual(self.koordconn.layer.categories[0].slug, "cadastral")
        self.assertEqual(self.koordconn.layer.data.crs, "EPSG:2193")
        self.assertEqual(self.koordconn.layer.data.fields[0].type, "geometry")
        # The following test changes form between Python 2.x and 3.x
        try:
            self.assertItemsEqual(self.koordconn.layer.tags, ['building', 'footprint', 'outline', 'structure'])
        except AttributeError:
            self.assertCountEqual(self.koordconn.layer.tags, ['building', 'footprint', 'outline', 'structure'])


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
