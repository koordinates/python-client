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
from __future__ import unicode_literals, absolute_import

import unittest
import uuid

import responses

#from koordinates import api
from koordinates import exceptions
from koordinates import Connection
from koordinates import PublishRequest

from response_data.responses_1 import layers_multiple_good_simulated_response
from response_data.responses_2 import layers_single_good_simulated_response
from response_data.responses_3 import sets_single_good_simulated_response
from response_data.responses_4 import sets_multiple_good_simulated_response
from response_data.responses_5 import layers_version_single_good_simulated_response
from response_data.responses_6 import layers_version_multiple_good_simulated_response
from response_data.responses_7 import publish_single_good_simulated_response
from response_data.responses_7 import publish_multiple_get_simulated_response


class TestKoordinatesPublishing(unittest.TestCase):

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = Connection('test')
        self.koordtestconn = Connection('test', host="test.koordinates.com")
        self.bad_koordconn = Connection('bad')

#   @responses.activate
#   def test_create_redaction(self):
#       the_response = layer_create_good_redaction_response

#       responses.add(responses.POST,
#                     self.koordconn.layer.get_url('REDACTION', 'POST', 'create'),
#                     body=the_response, status=201,
#                     content_type='application/json')

#       self.koordconn.redaction.name = api.Layer()
#       self.koordconn.redaction.name = "A Test Layer Name for Unit Testing"

#       self.koordconn.redaction.group.id = 263
#       self.koordconn.redaction.group.url = "https://test.koordinates.com/services/api/v1/groups/{}/".format(self.koordconn.redaction.group.id)
#       self.koordconn.redaction.group.name = "Wellington City Council"
#       self.koordconn.redaction.group.country = "NZ"

#       self.koordconn.redaction.data = api.Data(datasources = [api.DataSource(144355)])

#       self.koordconn.redaction.create()

#       self.assertEqual(self.koordconn.redaction.created_at.year, 2015)
#       self.assertEqual(self.koordconn.redaction.created_at.month,   6)
#       self.assertEqual(self.koordconn.redaction.created_at.day,    11)
#       self.assertEqual(self.koordconn.redaction.created_at.hour,   11)
#       self.assertEqual(self.koordconn.redaction.created_at.minute, 14)
#       self.assertEqual(self.koordconn.redaction.created_at.second, 10)
#       self.assertEqual(self.koordconn.redaction.created_by, 18504)

    @responses.activate
    def test_publish_get_by_id(self):
        the_response = publish_single_good_simulated_response

        publish_id = 2054
        responses.add(responses.GET,
                      self.koordconn.get_url('PUBLISH', 'GET', 'single', {'publish_id': publish_id}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.koordconn.publishes.get(publish_id)

        self.assertEqual(obj.state, "completed")
        self.assertEqual(obj.created_by.id, 18504)
        self.assertEqual(len(obj.items), 1)
        self.assertEqual(obj.items[0],
            'https://test.koordinates.com/services/api/v1/layers/8092/versions/9822/')
        self.assertEqual(obj.created_at.year, 2015)
        self.assertEqual(obj.created_at.month,   6)
        self.assertEqual(obj.created_at.day,     8)
        self.assertEqual(obj.created_at.hour,    3)
        self.assertEqual(obj.created_at.minute, 40)
        self.assertEqual(obj.created_at.second, 40)
        self.assertEqual(obj.created_by.id, 18504)

    @responses.activate
    def test_publish_get_all_rows(self):
        the_response = publish_multiple_get_simulated_response

        responses.add(responses.GET,
                      self.koordconn.get_url('PUBLISH', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_publish_records_returned = 0

        for pub_record in self.koordconn.publishes.list():
            if cnt_of_publish_records_returned == 0:
                self.assertEqual(pub_record.id, 2054)
                self.assertEqual(pub_record.error_strategy, 'abort')
            cnt_of_publish_records_returned += 1

        self.assertEqual(cnt_of_publish_records_returned, 7)


    @responses.activate
    def test_multipublish_resource_specification(self):
        the_response = '''{}'''
        responses.add(responses.POST,
                      self.koordtestconn.get_url('CONN', 'POST', 'publishmulti', optargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("")

        pr = PublishRequest(kwargs={'hostname':"test.koordinates.com"})
        pr.add_layer_to_publish(100, 1000)
        pr.add_layer_to_publish(101, 1001)
        pr.add_layer_to_publish(102, 1002)
        pr.add_table_to_publish(200, 2000)
        pr.add_table_to_publish(201, 2001)
        pr.add_table_to_publish(202, 2002)

        with self.assertRaises(exceptions.UnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr)

    @responses.activate
    def test_multipublish_bad_args(self):
        the_response = '''{}'''

        responses.add(responses.POST,
                      self.koordtestconn.get_url('CONN', 'POST', 'publishmulti', optargs={'hostname':"test.koordinates.com"}),
                      body=the_response, status=999,
                      content_type='application/json')


        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("")

        pr = PublishRequest([],[])

        with self.assertRaises(exceptions.UnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr)

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish("", 'Z')

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish(pr, 'Z')

        with self.assertRaises(exceptions.UnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr, 'together')

        with self.assertRaises(AssertionError):
            self.koordtestconn.multi_publish(pr, 'together', 'Z')

        with self.assertRaises(exceptions.UnexpectedServerResponse):
            #the Responses mocking will result in a 999 being returned
            self.koordtestconn.multi_publish(pr, 'together', 'abort')

    @responses.activate
    def test_publish_single_layer_version(self, layer_id=1474, version_id=4067):
        the_response = layers_version_single_good_simulated_response
        responses.add(responses.GET,
                      self.koordconn.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id}),
                      body=the_response, status=200,
                      content_type='application/json')



        #import pdb;pdb.set_trace()
        self.koordconn.version.get(1474, 4067)

        self.assertEqual(self.koordconn.version.id, 1474)
        self.assertEqual(self.koordconn.version.version_instance.id, 4067)

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
