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

import responses

from koordinates import Connection

from response_data.responses_1 import layers_multiple_good_simulated_response
from response_data.responses_2 import layers_single_good_simulated_response


class TestKoordinatesURLHandling(unittest.TestCase):

    def contains_substring(self, strtosearch, strtosearchfor):
        return strtosearch.lower().find(strtosearchfor) > -1

    def setUp(self):
        self.koordconn = Connection('test')
        self.koordtestconn = Connection('test', host="test.koordinates.com")
        self.bad_koordconn = Connection('bad')

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
