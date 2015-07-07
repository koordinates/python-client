# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.catalog` module.
"""
from __future__ import unicode_literals, absolute_import

import unittest

import responses

from koordinates import Client, Table, Layer, Set

from response_data.catalog import response_1


class CatalogTests(unittest.TestCase):

    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')

    @responses.activate
    def test_result_classes(self):
        responses.add(responses.GET,
                      self.client.get_url('CATALOG', 'GET', 'multi'),
                      body=response_1, status=200,
                      content_type='application/json')

        results = list(self.client.catalog.list())
        self.assertEqual(len(results), 14)

        self.assert_(isinstance(results[0], Table))
        self.assert_(isinstance(results[2], Layer))
        # TODO: Document
        self.assert_(isinstance(results[7], dict))
        self.assert_("/documents/" in results[7]["url"])
        self.assert_(isinstance(results[12], Set))

    @responses.activate
    def test_latest(self):
        responses.add(responses.GET,
                      self.client.get_url('CATALOG', 'GET', 'latest'),
                      body=response_1, status=200,
                      content_type='application/json')

        results = list(self.client.catalog.list_latest())
        self.assertEqual(len(results), 14)

        results = list(self.client.catalog.list_latest().filter(version__status='importing'))
        self.assertEqual(len(results), 14)

