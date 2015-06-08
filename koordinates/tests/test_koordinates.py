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


class TestKoordinates(unittest.TestCase):

    pwd = getpass()

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinates.pwd)
        self.koordtestconn = api.Connection('rshea@thecubagroup.com',
                                        TestKoordinates.pwd, 
                                        host="test.koordinates.com")
        invalid_password = str(uuid.uuid1())
        self.bad_koordconn = api.Connection('rshea@thecubagroup.com',
                                            invalid_password)

    def test_instantiate_group_class(self):
        g = api.Group(99, "http//example.com", "Group Name", "NZ")
        self.assertEqual(g.id, 99)
        self.assertTrue(self.contains_substring(g.url, "example"))
        self.assertEqual(g.name, "Group Name")
        self.assertEqual(g.country, "NZ")

    def test_instantiate_data_class(self):
        d = api.Data(None, "EPSG:2193",[],[],"GEOMETRY", [])
        self.assertEqual(d.encoding, None)
        self.assertEqual(d.crs, "EPSG:2193")
        self.assertEqual(d.geometry_field, "GEOMETRY")


    def test_instantiate_datasource_class(self):
        ds = api.DataSource(99)
        self.assertEqual(ds.id, 99)
        
    def test_instantiate_category_class(self):
        ca = api.Category("Category Name Test 0", "cadastral")
        self.assertEqual(ca.name, "Category Name Test 0")
        self.assertEqual(ca.slug, "cadastral")

        
    def test_instantiate_licence_class(self):
        li = api.License(99, 
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
        m = api.Metadata("https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/iso/",
                         "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
                         "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/")
                
        self.assertEqual(m.iso, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/iso/")
        self.assertEqual(m.dc, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/")
        self.assertEqual(m.native, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/")
        
    def test_instantiate_field_class(self):
        f = api.Field("Field Name", "integer")
        self.assertEqual(f.name, "Field Name")
        self.assertEqual(f.type, "integer")
        
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
                                                     TestKoordinates.pwd,
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
                                                         TestKoordinates.pwd,
                                                         test_host_name,
                                                         api_version=test_api_version)

            self.koordconnaltapiversion.layer.get(id)

    @responses.activate
    def test_get_layerset_bad_auth_check_status(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.layer.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            for layer in self.bad_koordconn.layer.get_list().execute_get_list():
                pass
        except koordexceptions.KoordinatesNotAuthorised:
            pass

        self.assertTrue(self.bad_koordconn.layer._raw_response.status_code,
                        401)

    @responses.activate
    def test_get_layerset_bad_auth_check_exception(self):
        the_response = '''{"detail": "Authentication credentials were not provided."}'''

        responses.add(responses.GET,
                      self.bad_koordconn.layer.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=401,
                      content_type='application/json')

        with self.assertRaises(koordexceptions.KoordinatesNotAuthorised):
            for layer in self.bad_koordconn.layer.get_list().execute_get_list():
                pass

    @responses.activate
    def test_get_layerset_returns_all_rows(self):
        the_response = layers_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_layers_returned = 0

        for layer in self.koordconn.layer.get_list().execute_get_list():
            cnt_of_layers_returned += 1

        self.assertEqual(cnt_of_layers_returned, 100)

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
#       self.koordconnalthost = api.Connection('rshea@thecubagroup.com',
#                                              TestKoordinates.pwd,
#                                              test_host_name)

#       self.koordconnalthost.layer.get_list().filter(filter_value).order_by(order_by_key)

#       parsedurl = urlparse(self.koordconnalthost.layer.url)

#       self.assertTrue(self.contains_substring(parsedurl.hostname, test_host_name))
#       self.assertEqual(parsedurl.hostname, test_host_name)

    @responses.activate
    def test_get_layerset_filter_and_sort(self):

        filter_value = str(uuid.uuid1())
        order_by_key = 'name'
        self.koordconn.layer.get_list().filter(filter_value).order_by(order_by_key)

        parsedurl = urlparse(self.koordconn.layer._url)

        self.assertTrue(self.contains_substring(parsedurl.query, filter_value))
        self.assertTrue(self.contains_substring(parsedurl.query, order_by_key))

    @responses.activate
    def test_get_layer_with_timeout(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id': id}),
                      body=the_response, status=504,
                      content_type='application/json')

        with self.assertRaises(koordexceptions.KoordinatesServerTimeOut):
            self.koordconn.layer.get(id)

    @responses.activate
    def test_get_layer_with_rate_limiting(self, id=1474):

        the_response = "{}"
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id': id}),
                      body=the_response, status=429,
                      content_type='application/json')

        with self.assertRaises(koordexceptions.KoordinatesRateLimitExceeded):
            self.koordconn.layer.get(id)

#   @responses.activate
#   def test_layer_import(self):

#       the_response = layers_single_good_simulated_response
#       #import pdb;pdb.set_trace()
#       dbgvalue = self.koordtestconn.version.get_url('VERSION', 'POST', 'import', {'layer_id': 999})
#       responses.add(responses.GET,
#                     self.koordtestconn.version.get_url('VERSION', 'POST', 'import', {'layer_id': 999}),
#                     body=the_response, status=200,
#                     content_type='application/json')

#       self.koordtestconn.version.import_version(999)

    @responses.activate
    def test_layer_hierarchy_of_classes(self):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id': 1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.layer.get(1474)
        self.assertEqual(self.koordconn.layer.categories[0].slug, "cadastral")
        self.assertEqual(self.koordconn.layer.data.crs, "EPSG:2193")
        self.assertEqual(self.koordconn.layer.data.fields[0].type, "geometry")
        # The following test changes form between Python 2.x and 3.x
        try:
            self.assertItemsEqual(self.koordconn.layer.tags, ['building', 'footprint', 'outline', 'structure'])
        except AttributeError:
            self.assertCountEqual(self.koordconn.layer.tags, ['building', 'footprint', 'outline', 'structure'])

    @responses.activate
    def test_layer_date_conversion(self, id=1474):

        the_response = layers_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.layer.get(id)
        self.assertEqual(self.koordconn.layer.first_published_at.year, 2010)
        self.assertEqual(self.koordconn.layer.first_published_at.month,   6)
        self.assertEqual(self.koordconn.layer.first_published_at.day,    21)
        self.assertEqual(self.koordconn.layer.first_published_at.hour,    5)
        self.assertEqual(self.koordconn.layer.first_published_at.minute,  5)
        self.assertEqual(self.koordconn.layer.first_published_at.second,  5)

        self.assertEqual(self.koordconn.layer.collected_at[0].year,    1996)
        self.assertEqual(self.koordconn.layer.collected_at[0].month,     12)
        self.assertEqual(self.koordconn.layer.collected_at[0].day,       31)

        self.assertEqual(self.koordconn.layer.collected_at[1].year,    2012)
        self.assertEqual(self.koordconn.layer.collected_at[1].month,      5)
        self.assertEqual(self.koordconn.layer.collected_at[1].day,        1)
        self.assertEqual(self.koordconn.layer.collected_at[1].hour,       0)
        self.assertEqual(self.koordconn.layer.collected_at[1].minute,     0)
        self.assertEqual(self.koordconn.layer.collected_at[1].second,     0)

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
                self.bad_koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':id}),
                      body=the_response, status=401,
                      content_type='application/json')

        try:
            self.bad_koordconn.layer.get(id)
        except:
            pass

        self.assertEqual(self.bad_koordconn.layer._raw_response.status_code,
                         401)

    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = layers_single_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.layer.get(id)

        self.assertEqual(self.koordconn.layer.name,
                         "Wellington City Building Footprints")
        self.assertEqual(self.koordconn.layer._raw_response.status_code,
                         200)

#   @responses.activate
#   def test_get_all_layer_version_by_layer_id(self, layer_id=1474, version_id=4067):

#       the_response = layers_version_single_good_simulated_response

#       responses.add(responses.GET,
#                     self.koordconn.version.get_url('VERSION','GET', 'multi', {'layer_id':layer_id}),
#                     body=the_response, status=200,
#                     content_type='application/json')

#       #import pdb; pdb.set_trace()
#       cnt_of_versions_returned = 0

#       for version in self.koordconn.version.get_list(layer_id=layer_id).execute_get_list():
#           cnt_of_versions_returned += 1

#       self.assertEqual(cnt_of_versions_returned, 2)


#       '''
#       self.assertEqual(self.koordconn.layer.id, layer_id)
#       self.assertEqual(self.koordconn.layer.version.id, version_id)
#       self.assertEqual(self.koordconn.layer.version.status, "ok")
#       self.assertEqual(self.koordconn.layer.version.created_by, 2879)
#       self.assertEqual(self.koordconn.layer.version._raw_response.status_code, 200)
#       '''

    @responses.activate
    def test_get_layer_by_id_and_create_attribute_with_reserved_name(self, id=1474):
        '''
        Tests to see whether an attribute name which is reserved
        causes the KoordinatesAttributeNameIsReserved exception
        to be raised
        '''

        the_response = '''{"id":1474, "version":"foobar"}'''
        responses.add(responses.GET,
                      self.koordconn.layer.get_url('LAYER', 'GET', 'single', {'layer_id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        with self.assertRaises(koordexceptions.KoordinatesAttributeNameIsReserved):
            self.koordconn.layer.get(id)

    @responses.activate
    def test_get_set_by_id(self, id=1474):

        the_response = sets_single_good_simulated_response


        responses.add(responses.GET,
                      self.koordconn.set.get_url('SET', 'GET', 'single', {'set_id':id}),
                      body=the_response, status=200,
                      content_type='application/json')

        self.koordconn.set.get(id)

        self.assertEqual(self.koordconn.set.title,
                         "Ultra Fast Broadband Initiative Coverage")
        self.assertEqual(self.koordconn.set.group.name,
                         "New Zealand Broadband Map")
        self.assertEqual(self.koordconn.set.url_html,
                         "https://koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/")
        self.assertEqual(self.koordconn.set._raw_response.status_code,
                         200)

    @responses.activate
    def test_get_set_set_returns_all_rows(self):
        the_response = sets_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.koordconn.layer.get_url('SET', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_sets_returned = 0

        for layer in self.koordconn.set.get_list().execute_get_list():
            cnt_of_sets_returned += 1

        self.assertEqual(cnt_of_sets_returned, 2)

    @responses.activate
    def test_multipublish_resource_specification(self):
        the_response = '''{}''' 
        responses.add(responses.POST,
                      self.koordtestconn.get_url('CONN', 'POST', 'publishmulti', kwargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.publish("")

        pr = api.PublishRequest(kwargs={'hostname':"test.koordinates.com"})
        pr.add_layer_to_publish(100, 1000)
        pr.add_layer_to_publish(101, 1001)
        pr.add_layer_to_publish(102, 1002)
        pr.add_table_to_publish(200, 2000)
        pr.add_table_to_publish(201, 2001)
        pr.add_table_to_publish(202, 2002)

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.publish(pr)

    @responses.activate
    def test_multipublish_bad_args(self):
        the_response = '''{}''' 

        responses.add(responses.POST,
                      self.koordtestconn.layer.get_url('CONN', 'POST', 'publishmulti', kwargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.publish("")

        pr = api.PublishRequest([],[])

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.publish(pr)

        with self.assertRaises(AssertionError):
            self.koordtestconn.publish("", 'Z')

        with self.assertRaises(AssertionError):
            self.koordtestconn.publish(pr, 'Z')

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.publish(pr, 'together')

        with self.assertRaises(AssertionError):
            self.koordtestconn.publish(pr, 'together', 'Z')

        with self.assertRaises(koordexceptions.KoordinatesUnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.publish(pr, 'together', 'abort')

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
