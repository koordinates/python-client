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

from koordinates import exceptions
from koordinates import Client


class TestKoordinatesURLHandling(unittest.TestCase):
    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.client = Client("koordinates.com", 'test')
        self.testclient = Client("test.koordinates.com", 'test')

    def test_sets_url(self):
        self.assertEqual(self.client.get_url('SET', 'GET', 'single', {'id':999}),
                        '''https://koordinates.com/services/api/v1/sets/999/''')

    def test_sets_domain_url(self):
        self.assertEqual(self.testclient.get_url('SET', 'GET', 'single', {'id':999}),
                        '''https://test.koordinates.com/services/api/v1/sets/999/''')

    def test_sets_multi_url(self):
        self.assertEqual(self.client.get_url('SET', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/sets/''')

    def test_layers_url(self):
        self.assertEqual(self.client.get_url('LAYER', 'GET', 'single', {'id':999}),
                        '''https://koordinates.com/services/api/v1/layers/999/''')

    def test_layers_multi_url(self):
        self.assertEqual(self.client.get_url('LAYER', 'GET', 'multi'),
                        '''https://koordinates.com/services/api/v1/layers/''')

    def test_layer_versions_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.client.get_url('VERSION', 'GET', 'single', {'layer_id':layer_id, 'version_id':version_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/4067/''')

    def test_layer_versions_multi_url(self, layer_id=1494, version_id=4067):
        self.assertEqual(self.client.get_url('VERSION', 'GET', 'multi', {'layer_id':layer_id}),
                        '''https://koordinates.com/services/api/v1/layers/1494/versions/''')

    def test_api_version_in_url_when_valid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        client_altapiversion = Client(token='test', host=test_host_name, api_version='UNITTESTINGONLY')

        self.assertEqual(client_altapiversion.get_url('LAYER', 'GET', 'multi', {'hostname':test_host_name, 'api_version':'UNITTESTINGONLY'}),
                        '''https://''' + test_host_name + '''/services/api/UNITTESTINGONLY/layers/''')

    def test_api_version_in_url_when_invalid(self):
        test_domain = str(uuid.uuid1()).replace("-", "")
        test_api_version = str(uuid.uuid1()).replace("-", "")
        test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
        with self.assertRaises(exceptions.InvalidAPIVersion):
            client_altapiversion = Client(host=test_host_name, api_version=test_api_version)
            client_altapiversion.layer.get(1)


if __name__ == '__main__':
    unittest.main()
