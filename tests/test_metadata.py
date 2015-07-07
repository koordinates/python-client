# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.metadata` module.
"""
from __future__ import unicode_literals, absolute_import

import unittest

import responses
import six

from koordinates import Client, Metadata, Layer

from response_data.responses_5 import layers_version_single_good_simulated_response


class MetadataTests(unittest.TestCase):

    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')

    @responses.activate
    def test_existing(self):
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')

        responses.add(responses.GET,
                      "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
                      body="<dc>", status=200,
                      content_type='text/xml')
        responses.add(responses.GET,
                      "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
                      body="<native>", status=200,
                      content_type='text/xml')

        layer = self.client.layers.get(1474)

        self.assert_(isinstance(layer.metadata, Metadata))
        self.assertEqual(layer.metadata.dc, "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/")
        self.assertEqual(set(layer.metadata.get_formats()), set(["iso", "dc"]))
        self.assertEqual(layer.metadata._is_bound, True)

    @responses.activate
    def test_get_xml(self):
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')

        responses.add(responses.GET,
                      "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
                      body="<dc>", status=200,
                      content_type='text/xml')
        responses.add(responses.GET,
                      "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
                      body="<native>", status=200,
                      content_type='text/xml')

        layer = self.client.layers.get(1474)

        s = six.BytesIO()
        layer.metadata.get_xml(s, layer.metadata.FORMAT_DC)
        self.assertEqual(s.getvalue().decode("utf-8"), "<dc>")

        s = six.BytesIO()
        layer.metadata.get_xml(s, layer.metadata.FORMAT_NATIVE)
        self.assertEqual(s.getvalue().decode("utf-8"), "<native>")

    @responses.activate
    def test_set_xml(self):
        lv_url = self.client.get_url('VERSION', 'GET', 'single', {'layer_id': 1474, 'version_id': 4067})
        responses.add(responses.GET,
                      lv_url,
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')

        responses.add(responses.POST,
                      lv_url + 'metadata/',
                      body="", status=204,
                      adding_headers={"Location": lv_url + 'metadata/'})

        layer = self.client.layers.get_version(1474, 4067)

        old_meta = layer.metadata

        s = six.StringIO("<test>")
        layer.set_metadata(s)

        self.assertEqual(s.getvalue(), "<test>")

        # load layer, set metadata, reload layer
        self.assertEqual(len(responses.calls), 3)

        self.assert_(isinstance(responses.calls[1].request.body, six.StringIO))
        self.assertEqual(responses.calls[1].request.body.getvalue(), "<test>")

        self.assert_(isinstance(layer.metadata, Metadata))
        self.assert_(layer.metadata is not old_meta)

    @responses.activate
    def test_set_xml_manager(self):
        lv_url = self.client.get_url('VERSION', 'GET', 'single', {'layer_id': 1474, 'version_id': 4067})
        responses.add(responses.GET,
                      lv_url,
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')

        responses.add(responses.POST,
                      lv_url + 'metadata/',
                      body="", status=204,
                      adding_headers={"Location": lv_url + 'metadata/'})


        s = six.StringIO("<test>")
        r = self.client.layers.set_metadata(1474, 4067, s)

        self.assertEqual(len(responses.calls), 1)

        self.assert_(isinstance(responses.calls[0].request.body, six.StringIO))
        self.assertEqual(responses.calls[0].request.body.getvalue(), "<test>")

        self.assertEqual(r, None)


