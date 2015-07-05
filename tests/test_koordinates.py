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
from __future__ import unicode_literals, absolute_import

import unittest
import uuid
from six.moves import urllib

import responses

import koordinates
from koordinates import exceptions
from koordinates import Connection

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
        self.koordconn = Connection(token='test')
        self.koordtestconn = Connection(token='test', host="test.koordinates.com")
        self.bad_koordconn = Connection(token='bad')

    def test_instantiate_group_class(self):
        g = koordinates.Group(id=99, url="http//example.com", name="Group Name", country="NZ")
        self.assertEqual(g.id, 99)
        self.assertTrue(self.contains_substring(g.url, "example"))
        self.assertEqual(g.name, "Group Name")
        self.assertEqual(g.country, "NZ")

    def test_instantiate_data_class(self):
        d = koordinates.Data(None, "EPSG:2193",[],[],"GEOMETRY", [])
        self.assertEqual(d.encoding, None)
        self.assertEqual(d.crs, "EPSG:2193")
        self.assertEqual(d.geometry_field, "GEOMETRY")


    def test_instantiate_datasource_class(self):
        ds = koordinates.Datasource(99)
        self.assertEqual(ds.id, 99)

    def test_instantiate_category_class(self):
        ca = koordinates.Category("Category Name Test 0", "cadastral")
        self.assertEqual(ca.name, "Category Name Test 0")
        self.assertEqual(ca.slug, "cadastral")


    def test_instantiate_licence_class(self):
        li = koordinates.License(99,
                        "Creative Commons Attribution 3.0 New Zealand",
                        "cc-by",
                        "nz",
                        "3.0",
                        "https://koordinates.com/services/api/v1/licenses/9/",
                        "https://koordinates.com/license/attribution-3-0-new-zealand/")
        self.assertEqual(li.id, 99)
        self.assertEqual(li.title, "Creative Commons Attribution 3.0 New Zealand")
        self.assertEqual(li.type, 'cc-by')
        self.assertEqual(li.jurisdiction, "nz")
        self.assertEqual(li.version, "3.0")
        self.assertEqual(li.url, "https://koordinates.com/services/api/v1/licenses/9/")
        self.assertEqual(li.url_html, "https://koordinates.com/license/attribution-3-0-new-zealand/")

    def test_instantiate_metadata_class(self):
        m = koordinates.Metadata("https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/iso/",
                         "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
                         "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/")

        self.assertEqual(m.iso, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/iso/")
        self.assertEqual(m.dc, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/")
        self.assertEqual(m.native, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/")

    def test_instantiate_field_class(self):
        f = koordinates.Field("Field Name", "integer")
        self.assertEqual(f.name, "Field Name")
        self.assertEqual(f.type, "integer")

    @responses.activate
    def test_get_layerset_bad_auth_check_status(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')


        #TODO ideally we would drill down into exception and test actual HTTP return
        #self.assertTrue(self.bad_koordconn.layer._raw_response.status_code,
        #                401)
        #TODO ideally we would drill down into exception and test actual HTTP return
        import requests
        with self.assertRaises(requests.exceptions.HTTPError):
            for layer in self.bad_koordconn.layers.list():
                pass

    @unittest.skip("FIXME")
    @responses.activate
    def test_create_layer(self):
        the_response = layer_create_good_simulated_response

        responses.add(responses.POST,
                      self.koordconn.get_url('LAYER', 'POST', 'create'),
                      body=the_response, status=201,
                      content_type='application/json')

        obj_lyr = koordinates.Layer()
        obj_lyr.name = "A Test Layer Name for Unit Testing"

        obj_lyr.group = 263
        obj_lyr.data = koordinates.Data(datasources = [koordinates.Datasource(144355)])

        result_layer = self.koordconn.layers.create(obj_lyr)
        self.assert_(result_layer is obj_lyr)
        self.assertEqual(obj_lyr.created_at.year, 2015)
        self.assertEqual(obj_lyr.created_at.month,   6)
        self.assertEqual(obj_lyr.created_at.day,    11)
        self.assertEqual(obj_lyr.created_at.hour,   11)
        self.assertEqual(obj_lyr.created_at.minute, 14)
        self.assertEqual(obj_lyr.created_at.second, 10)
        self.assertEqual(obj_lyr.created_by, 18504)

        self.assertEqual(obj_lyr.group.id, 263)
        self.assertEqual(obj_lyr.group.url, "https://test.koordinates.com/services/api/v1/groups/{}/".format(obj_lyr.group.id))
        self.assertEqual(obj_lyr.group.name, "Wellington City Council")
        self.assertEqual(obj_lyr.group.country, "NZ")

    @responses.activate
    def test_get_layerset_bad_auth_check_exception(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')

        #with self.assertRaises(exceptions.NotAuthorised):
        #TODO ideally we would drill down into exception and test actual HTTP return
        import requests
        with self.assertRaises(requests.exceptions.HTTPError):
            for layer in self.bad_koordconn.layers.list():
                pass

    @responses.activate
    def test_get_layerset_returns_all_rows(self):
        the_response = layers_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_layers_returned = 0

        #import pdb;pdb.set_trace()
        for layer in self.koordconn.layers.list():
            cnt_of_layers_returned += 1

        #import pdb;pdb.set_trace()
        self.assertEqual(cnt_of_layers_returned, 100)

    @responses.activate
    def test_get_draft_layerset_returns_all_rows(self):
        the_response = good_multi_layers_drafts_response

        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'multidraft'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_draft_layers_returned = 0

        for layer in self.koordconn.layers.list_drafts():
            cnt_of_draft_layers_returned += 1

        self.assertEqual(cnt_of_draft_layers_returned, 12)

    @responses.activate
    def test_get_draft_layerset_test_characteristics_of_response(self):
        the_response = good_multi_layers_drafts_response

        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'multidraft'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_draft_layers_returned = 0

        #import pdb;pdb.set_trace()
        for layer in self.koordconn.layers.list_drafts():
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
#       self.koordconnalthost = Connection('test', test_host_name)

#       self.koordconnalthost.layer.get_list().filter(filter_value).order_by(order_by_key)

#       parsedurl = urllib.parse.urlparse(self.koordconnalthost.layer.url)

#       self.assertTrue(self.contains_substring(parsedurl.hostname, test_host_name))
#       self.assertEqual(parsedurl.hostname, test_host_name)

    @responses.activate
    def test_get_layerset_filter(self):
        q = self.koordconn.layers.list().filter(kind='vector')
        parsedurl = urllib.parse.urlparse(q._to_url())
        self.assertTrue(self.contains_substring(parsedurl.query, 'kind=vector'))

    @responses.activate
    def test_get_layerset_sort(self):
        q = self.koordconn.layers.list().order_by('name')
        parsedurl = urllib.parse.urlparse(q._to_url())
        self.assertTrue(self.contains_substring(parsedurl.query, 'sort=name'))

    @responses.activate
    def test_get_layer_with_timeout(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'single', {'id': id}),
                      body=the_response, status=504,
                      content_type='application/json')

        #with self.assertRaises(exceptions.ServerTimeOut):
        #TODO ideally we would drill down into exception and test actual HTTP return
        import requests
        with self.assertRaises(requests.exceptions.HTTPError):
            obj = self.koordconn.layers.get(id)

    @responses.activate
    def test_get_layer_with_rate_limiting(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'single', {'id': id}),
                      body=the_response, status=429,
                      content_type='application/json')

        #with self.assertRaises(exceptions.RateLimitExceeded):
        #TODO ideally we would drill down into exception and test actual HTTP return
        import requests
        with self.assertRaises(requests.exceptions.HTTPError):
            obj = self.koordconn.layers.get(id)

    @responses.activate
    def test_layer_import(self):

        the_response = layers_single_good_simulated_response
        layer_id = 999
        version_id = 998
        dbgvalue = self.koordtestconn.version.get_url('VERSION', 'POST', 'import', optargs={'version_id': version_id,'layer_id': layer_id, 'hostname':"test.koordinates.com"})
        responses.add(responses.POST,
                      self.koordtestconn.version.get_url('VERSION', 'POST', 'import', optargs={'version_id': version_id,'layer_id': layer_id, 'hostname':"test.koordinates.com"}),
                      body=the_response, status=202,
                      content_type='application/json')

        self.koordtestconn.version.import_version(layer_id, version_id)

    @unittest.skip("FIXME")
    @responses.activate
    def test_layer_hierarchy_of_classes(self):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.koordconn.layers.get(1474)
        self.assertEqual(obj.categories[0].slug, "cadastral")
        self.assertEqual(obj.data.crs, "EPSG:2193")
        self.assertEqual(obj.data.fields[0].type, "geometry")
        # The following test changes form between Python 2.x and 3.x
        try:
            self.assertItemsEqual(obj.tags, ['building', 'footprint', 'outline', 'structure'])
        except AttributeError:
            self.assertCountEqual(obj.tags, ['building', 'footprint', 'outline', 'structure'])

    @unittest.skip("FIXME")
    @responses.activate
    def test_layer_date_conversion(self, id=1474):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        #import pdb;pdb.set_trace()
        obj = self.koordconn.layers.get(id)
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

    @unittest.skip("FIXME")
    @responses.activate
    def test_get_layerset_bad_filter_and_sort(self):
        with self.assertRaises(exceptions.NotAValidBasisForOrdering):
            self.koordconn.layers.list().filter(bad_attribute=True)

    @responses.activate
    def test_get_layerset_bad_sort(self):
        with self.assertRaises(exceptions.NotAValidBasisForOrdering):
            self.koordconn.layers.list().order_by('bad_attribute')

    @responses.activate
    def test_get_layer_by_id_bad_auth(self, id=1474):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                self.bad_koordconn.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            layer_obj = self.bad_koordconn.layers.get(id)
        except:
            pass

        #TODO ideally we would drill down into exception and test actual HTTP return
        import requests
        with self.assertRaises(requests.exceptions.HTTPError):
            layer_obj = self.bad_koordconn.layers.get(id)
        #self.assertEqual(self.bad_koordconn.layer._raw_response.status_code,
        #                 401)

    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = layers_single_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.get_url('LAYER', 'GET', 'single', {'id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.koordconn.layers.get(id)

        self.assertEqual(obj.name,
                         "Wellington City Building Footprints")
        #There is no way to do this test any more - it is implict
        #since we started using 'raise_for_status'
        #self.assertEqual(obj._raw_response.status_code,
        #                 200)

    @responses.activate
    def test_get_all_layer_version_by_layer_id(self, layer_id=1474, version_id=4067):

        the_response = single_layer_all_versions_good_response

        responses.add(responses.GET,
                      self.koordconn.version.get_url('VERSION','GET', 'multi', {'layer_id':layer_id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_versions_returned = 0

        for version in self.koordconn.version.get_list(layer_id=layer_id).execute_get_list():
            cnt_of_versions_returned += 1

        self.assertEqual(cnt_of_versions_returned, 2)


#       '''
#       self.assertEqual(self.koordconn.layer.id, layer_id)
#       self.assertEqual(self.koordconn.layer.version.id, version_id)
#       self.assertEqual(self.koordconn.layer.version.status, "ok")
#       self.assertEqual(self.koordconn.layer.version.created_by, 2879)
#       self.assertEqual(self.koordconn.layer.version._raw_response.status_code, 200)
#       '''

#   '''
#   The following test is redundant since we started to use "non-dynamic" instance
#   create by default. I'm just going to leave it here until the corresponding
#   "dynamic" instance creation code is removed entirely (as oposed to just branched
#   around) in api.py then the test can be removed entirely
#   @responses.activate
#   def test_get_layer_by_id_and_create_attribute_with_reserved_name(self, id=1474):
#       '''
#       Tests to see whether an attribute name which is reserved
#       causes the KoordinatesAttributeNameIsReserved exception
#       to be raised
#       '''

#       the_response = '''{"id":1474, "version":"foobar"}'''
#       responses.add(responses.GET,
#                     self.koordconn.get_url('LAYER', 'GET', 'single', {'layer_id':id}),
#                     body=the_response, status=200,
#                     content_type='application/json')
#       import pdb;pdb.set_trace()
#       with self.assertRaises(exceptions.AttributeNameIsReserved):
#           self.koordconn.layer.get(id)


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
