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

import unittest
import uuid

from koordinates import api
from koordinates import utils
from koordinates import exceptions

from response_data.responses_1 import layers_multiple_good_simulated_response
from response_data.responses_2 import layers_single_good_simulated_response
from response_data.responses_3 import sets_single_good_simulated_response
from response_data.responses_4 import sets_multiple_good_simulated_response
from response_data.responses_5 import layers_version_single_good_simulated_response
from response_data.responses_6 import layers_version_multiple_good_simulated_response


class TestKoordinatesURLHandling(unittest.TestCase):
    pwd = 'password'

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

    def test_sets_url(self):
        self.assertEqual(self.koordconn.set.get_url('SET', 'GET', 'single', {'set_id':999}),
                        '''https://koordinates.com/services/api/v1/sets/999/''')

    def test_sets_domain_url(self):
        self.assertEqual(self.koordtestconn.set.get_url('SET', 'GET', 'single', {'set_id':999}),
                        '''https://test.koordinates.com/services/api/v1/sets/999/''')

    def test_sets_multi_url(self):
        self.assertEqual(self.koordconn.set.get_url('SET', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/sets/''')

    def test_layers_url(self):
        self.assertEqual(self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':999}),
                        '''https://koordinates.com/services/api/v1/layers/999/''')

    def test_layers_multi_url(self):
        self.assertEqual(self.koordconn.layer.get_url('LAYER', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/layers/''')

    def test_layer_versions_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.koordconn.layer.get_url('VERSION', 'GET', 'single', {'layer_id':layer_id, 'version_id':version_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/4067/''')

    def test_layer_versions_multi_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.koordconn.layer.get_url('VERSION', 'GET', 'multi', {'layer_id':layer_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/''')

    def test_api_version_in_url_when_valid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        self.koordconnaltapiversion = api.Connection('rshea@thecubagroup.com',
                                                     TestKoordinatesURLHandling.pwd,
                                                     test_host_name,
                                                     api_version='UNITTESTINGONLY')

        self.assertEqual(self.koordconnaltapiversion.layer.get_url('LAYER', 'GET', 'multi', {'hostname':test_host_name, 'api_version':'UNITTESTINGONLY'}),
                        '''https://''' + test_host_name + '''/services/api/UNITTESTINGONLY/layers/''')

    def test_api_version_in_url_when_invalid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_api_version = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        with self.assertRaises(exceptions.InvalidAPIVersion):
            self.koordconnaltapiversion = api.Connection('rshea@thecubagroup.com',
                                                         TestKoordinatesURLHandling.pwd,
                                                         test_host_name,
                                                         api_version=test_api_version)

            self.koordconnaltapiversion.layer.get(id)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
