#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General tests.
"""
from __future__ import unicode_literals, absolute_import

import unittest
from six.moves import urllib

import responses

import koordinates
from koordinates import exceptions
from koordinates import Client
from koordinates import layers

from response_data.responses_1 import layers_multiple_good_simulated_response
from response_data.responses_2 import layers_single_good_simulated_response
from response_data.responses_5 import layers_version_single_good_simulated_response
from response_data.responses_6 import layers_version_multiple_good_simulated_response
from response_data.responses_8 import layer_create_good_simulated_response
from response_data.responses_9 import single_layer_all_versions_good_response
from response_data.responses_9 import good_multi_layers_drafts_response


class TestKoordinates(unittest.TestCase):
    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.client = Client(token='test', host='koordinates.com')
        self.test_client = Client(token='test', host="test.koordinates.com")
        self.bad_client = Client(token='bad', host='koordinates.com')

    def test_instantiate_group_class(self):
        g = koordinates.Group(id=99, url="http//example.com", name="Group Name", country="NZ")
        self.assertEqual(g.id, 99)
        self.assertTrue(self.contains_substring(g.url, "example"))
        self.assertEqual(g.name, "Group Name")
        self.assertEqual(g.country, "NZ")

    def test_instantiate_data_class(self):
        d = layers.LayerData(encoding=None,
                            crs="EPSG:2193",
                            geometry_field="GEOMETRY"
        )
        self.assertEqual(d.encoding, None)
        self.assertEqual(d.crs, "EPSG:2193")
        self.assertEqual(d.geometry_field, "GEOMETRY")

    @unittest.skip("FIXME")
    def test_instantiate_datasource_class(self):
        ds = layers.Datasource(99)
        self.assertEqual(ds.id, 99)

    @unittest.skip("FIXME")
    def test_instantiate_field_class(self):
        f = koordinates.Field("Field Name", "integer")
        self.assertEqual(f.name, "Field Name")
        self.assertEqual(f.type, "integer")

    @responses.activate
    def test_get_layerset_bad_auth_check_status(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_client.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')


        with self.assertRaises(exceptions.AuthenticationError):
            for layer in self.bad_client.layers.list():
                pass

    @responses.activate
    def test_create_layer(self):
        the_response = layer_create_good_simulated_response

        responses.add(responses.POST,
                      self.client.get_url('LAYER', 'POST', 'create'),
                      body=the_response, status=201,
                      content_type='application/json')

        obj_lyr = koordinates.Layer()
        obj_lyr.name = "A Test Layer Name for Unit Testing"

        obj_lyr.group = 263
        obj_lyr.data = layers.LayerData(datasources = [144355])

        result_layer = self.client.layers.create(obj_lyr)
        self.assert_(result_layer is obj_lyr)
        self.assertEqual(obj_lyr.created_at.year, 2015)
        self.assertEqual(obj_lyr.created_at.month,   6)
        self.assertEqual(obj_lyr.created_at.day,    11)
        self.assertEqual(obj_lyr.created_at.hour,   11)
        self.assertEqual(obj_lyr.created_at.minute, 14)
        self.assertEqual(obj_lyr.created_at.second, 10)
        self.assertEqual(obj_lyr.created_by, 18504)

        # FIXME: API should return a full response
        # self.assertEqual(obj_lyr.group.id, 263)
        # self.assertEqual(obj_lyr.group.url, "https://test.koordinates.com/services/api/v1/groups/{}/".format(obj_lyr.group.id))
        # self.assertEqual(obj_lyr.group.name, "Wellington City Council")
        # self.assertEqual(obj_lyr.group.country, "NZ")

    @responses.activate
    def test_get_layerset_bad_auth_check_exception(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_client.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')

        with self.assertRaises(exceptions.AuthenticationError):
            for layer in self.bad_client.layers.list():
                pass

    @responses.activate
    def test_get_layerset_returns_all_rows(self):
        the_response = layers_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_layers_returned = 0

        #import pdb;pdb.set_trace()
        for layer in self.client.layers.list():
            cnt_of_layers_returned += 1

        #import pdb;pdb.set_trace()
        self.assertEqual(cnt_of_layers_returned, 100)

    @responses.activate
    def test_get_draft_layerset_returns_all_rows(self):
        the_response = good_multi_layers_drafts_response

        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'multidraft'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_draft_layers_returned = 0

        for layer in self.client.layers.list_drafts():
            cnt_of_draft_layers_returned += 1

        self.assertEqual(cnt_of_draft_layers_returned, 12)

    @responses.activate
    def test_get_draft_layerset_test_characteristics_of_response(self):
        the_response = good_multi_layers_drafts_response

        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'multidraft'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_draft_layers_returned = 0

        #import pdb;pdb.set_trace()
        for layer in self.client.layers.list_drafts():
            if cnt_of_draft_layers_returned == 0:
                self.assertEqual(layer.id, 7955)
                self.assertEqual(layer.name, "Built-Up Area")
                self.assertEqual(layer.first_published_at.year, 2015)
                self.assertEqual(layer.first_published_at.month, 4)
                self.assertEqual(layer.first_published_at.day, 21)
                self.assertEqual(layer.first_published_at.hour, 0)
                self.assertEqual(layer.first_published_at.minute, 59)
                self.assertEqual(layer.first_published_at.second, 55)
            if cnt_of_draft_layers_returned == 11:
                self.assertEqual(layer.id, 8113)
                self.assertEqual(layer.name, "shea-test-layer-14")
            cnt_of_draft_layers_returned += 1




    # This test is now impossible to conduct with the change in the way the
    # the URL templates are populated - part of which is that the hostname
    # is picked up at a higher level than previously. I'm putting this one
    # on ice until other things have stablilised at which point changes should
    # be made sufficient to allow this test or one of corresponding capability
#   @responses.activate
#   def test_get_layerset_with_non_default_host(self):

#       filter_value = str(uuid.uuid1())
#       test_domain = str(uuid.uuid1()).replace("-", "")
#       order_by_key = 'name'
#       test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
#       self.clientalthost = Client('test', test_host_name)

#       self.clientalthost.layer.get_list().filter(filter_value).order_by(order_by_key)

#       parsedurl = urllib.parse.urlparse(self.clientalthost.layer.url)

#       self.assertTrue(self.contains_substring(parsedurl.hostname, test_host_name))
#       self.assertEqual(parsedurl.hostname, test_host_name)

    @responses.activate
    def test_get_layerset_filter(self):
        q = self.client.layers.list().filter(kind='vector')
        parsedurl = urllib.parse.urlparse(q._to_url())
        self.assertTrue(self.contains_substring(parsedurl.query, 'kind=vector'))

    @responses.activate
    def test_get_layerset_sort(self):
        q = self.client.layers.list().order_by('name')
        parsedurl = urllib.parse.urlparse(q._to_url())
        self.assertTrue(self.contains_substring(parsedurl.query, 'sort=name'))

    @responses.activate
    def test_get_layer_with_timeout(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': id}),
                      body=the_response, status=504,
                      content_type='application/json')

        with self.assertRaises(exceptions.ServiceUnvailable):
            obj = self.client.layers.get(id)

    @responses.activate
    def test_get_layer_with_rate_limiting(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': id}),
                      body=the_response, status=429,
                      content_type='application/json')

        with self.assertRaises(exceptions.RateLimitExceeded):
            obj = self.client.layers.get(id)

    @responses.activate
    def test_layer_import(self):

        the_response = layers_single_good_simulated_response
        layer_id = 999
        version_id = 998
        responses.add(responses.POST,
                      self.test_client.get_url('VERSION', 'POST', 'import', {'version_id': version_id,'layer_id': layer_id}),
                      body=the_response, status=202,
                      content_type='application/json')

        self.test_client.layers.start_import(layer_id, version_id)

    @responses.activate
    def test_layer_hierarchy_of_classes(self):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.client.layers.get(1474)
        self.assertEqual(obj.categories[0]['slug'], "cadastral")
        self.assertEqual(obj.data.crs, "EPSG:2193")
        self.assertEqual(obj.data.fields[0]['type'], "geometry")
        # The following test changes form between Python 2.x and 3.x
        try:
            self.assertItemsEqual(obj.tags, ['building', 'footprint', 'outline', 'structure'])
        except AttributeError:
            self.assertCountEqual(obj.tags, ['building', 'footprint', 'outline', 'structure'])

    @responses.activate
    def test_layer_date_conversion(self, id=1474):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        #import pdb;pdb.set_trace()
        obj = self.client.layers.get(id)
        self.assertEqual(obj.first_published_at.year, 2010)
        self.assertEqual(obj.first_published_at.month,   6)
        self.assertEqual(obj.first_published_at.day,    21)
        self.assertEqual(obj.first_published_at.hour,    5)
        self.assertEqual(obj.first_published_at.minute,  5)
        self.assertEqual(obj.first_published_at.second,  5)

        self.assertEqual(obj.collected_at[0].year,    1996)
        self.assertEqual(obj.collected_at[0].month,     12)
        self.assertEqual(obj.collected_at[0].day,       31)

        self.assertEqual(obj.collected_at[1].year,    2012)
        self.assertEqual(obj.collected_at[1].month,      5)
        self.assertEqual(obj.collected_at[1].day,        1)
        self.assertEqual(obj.collected_at[1].hour,       0)
        self.assertEqual(obj.collected_at[1].minute,     0)
        self.assertEqual(obj.collected_at[1].second,     0)

    @responses.activate
    def test_get_layerset_bad_filter_and_sort(self):
        with self.assertRaises(exceptions.ClientValidationError):
            self.client.layers.list().filter(bad_attribute=True)

    @responses.activate
    def test_get_layerset_bad_sort(self):
        with self.assertRaises(exceptions.ClientValidationError):
            self.client.layers.list().order_by('bad_attribute')

    @responses.activate
    def test_get_layer_by_id_bad_auth(self, id=1474):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                self.bad_client.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            layer_obj = self.bad_client.layers.get(id)
        except:
            pass

        with self.assertRaises(exceptions.AuthenticationError):
            layer_obj = self.bad_client.layers.get(id)

    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = layers_single_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.client.layers.get(id)

        self.assertEqual(obj.name,
                         "Wellington City Building Footprints")
        #There is no way to do this test any more - it is implict
        #since we started using 'raise_for_status'
        #self.assertEqual(obj._raw_response.status_code,
        #                 200)

    @responses.activate
    def test_get_all_layer_version_by_layer_id(self):

        the_response = single_layer_all_versions_good_response

        responses.add(responses.GET,
                      self.client.get_url('VERSION','GET', 'multi', {'layer_id':1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_versions_returned = 0

        for version in self.client.layers.list_versions(layer_id=1474):
            cnt_of_versions_returned += 1

        self.assertEqual(cnt_of_versions_returned, 2)

        self.assertEqual(version.id, 32)
        self.assertEqual(version.status, "ok")
        self.assertEqual(version.created_by, 2879)


if __name__ == '__main__':
    unittest.main()
