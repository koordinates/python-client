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
from canned_responses_for_tests_3 import sets_single_good_simulated_response
from canned_responses_for_tests_4 import sets_multiple_good_simulated_response
from canned_responses_for_tests_5 import layers_version_single_good_simulated_response
from canned_responses_for_tests_6 import layers_version_multiple_good_simulated_response


def getpass():
    '''
    Prompt user for Password until there is a Connection object
    '''
    import getpass
    if ('CIRCLECI' in os.environ) and ('KPWD' in os.environ):
        return os.environ['KPWD']
    else:
        return(getpass.getpass('Please enter your Koordinates password: '))


class TestKoordinatesURLHandling(unittest.TestCase):

    pwd = getpass()

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = api.Connection('rshea@thecubagroup.com',
                                        __class__.pwd)
        self.koordtestconn = api.Connection('rshea@thecubagroup.com',
                                        __class__.pwd, 
                                        host="test.koordinates.com")
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = api.Connection('rshea@thecubagroup.com',
                                            invalid_password)

    def test_sets_url(self):
        self.assertEqual(self.koordconn.set.get_url('SET', 'GET', 'single', {'set_id':999}),
                        '''https://koordinates.com/services/api/v1/sets/999/''')

    def test_sets_url_template(self):
        self.assertEqual(self.koordconn.set.url_templates('SET', 'GET', 'single'),
                        '''https://{hostname}/services/api/{api_version}/sets/{set_id}/''')

    def test_sets_multi_url(self):
        self.assertEqual(self.koordconn.set.get_url('SET', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/sets/''')

    def test_layers_url(self):
        self.assertEqual(self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':999}),
                        '''https://koordinates.com/services/api/v1/layers/999/''')

    def test_layers_url_template(self):
        self.assertEqual(self.koordconn.layer.url_templates('LAYER', 'GET', 'single'),
                        '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/''')

    def test_layers_multi_url(self):
        self.assertEqual(self.koordconn.layer.get_url('LAYER', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/layers/''')

    def test_layer_versions_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.koordconn.layer.get_url('VERSION', 'GET', 'single', {'layer_id':layer_id, 'version_id':version_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/4067/''')

    def test_layer_versions_url_template(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.koordconn.layer.url_templates('VERSION', 'GET', 'single'),
                        '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/{version_id}/''')

    def test_layer_versions_multi_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.koordconn.layer.get_url('VERSION', 'GET', 'multi', {'layer_id':layer_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/''')

    def test_api_version_in_url_when_valid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        self.koordconnaltapiversion = api.Connection('rshea@thecubagroup.com',
                                                     __class__.pwd,
                                                     test_host_name,
                                                     api_version='UNITTESTINGONLY')

        self.assertEqual(self.koordconnaltapiversion.layer.get_url('LAYER', 'GET', 'multi', {'hostname':test_host_name, 'api_version':'UNITTESTINGONLY'}),
                        '''https://''' + test_host_name + '''/services/api/UNITTESTINGONLY/layers/''')

    def test_api_version_in_url_when_invalid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_api_version = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        with self.assertRaises(koordexceptions.KoordinatesInvalidAPIVersion):
            self.koordconnaltapiversion = api.Connection('rshea@thecubagroup.com',
                                                         __class__.pwd,
                                                         test_host_name,
                                                         api_version=test_api_version)

            self.koordconnaltapiversion.layer.get(id)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
