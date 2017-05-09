# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.metadata` module.
"""
from __future__ import unicode_literals, absolute_import

import os
import shutil
import tempfile

import pytest
import responses
import six

from koordinates import Client, Metadata

from .response_data.responses_5 import layers_version_single_good_simulated_response

@pytest.fixture
def client():
    return Client(token='test', host='test.koordinates.com')


@responses.activate
def test_existing(client):
    responses.add(responses.GET,
                  client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
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

    layer = client.layers.get(1474)

    assert isinstance(layer.metadata, Metadata)
    assert layer.metadata.dc == "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/"
    assert set(layer.metadata.get_formats()) == {'iso', 'dc'}
    assert layer.metadata._is_bound


@responses.activate
def test_get_xml(client):
    responses.add(responses.GET,
                  client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
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
    responses.add(responses.GET,
                  "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
                  body="<native>", status=200,
                  content_type='text/xml')

    layer = client.layers.get(1474)

    s = six.BytesIO()
    layer.metadata.get_xml(s, layer.metadata.FORMAT_DC)
    assert s.getvalue().decode("utf-8") == "<dc>"

    s = six.BytesIO()
    layer.metadata.get_xml(s, layer.metadata.FORMAT_NATIVE)
    assert s.getvalue().decode("utf-8") == "<native>"

    t = tempfile.mkdtemp()
    try:
        tfn = os.path.join(t, 'metadata.xml')
        layer.metadata.get_xml(tfn)

        with open(tfn, 'r') as tf:
            assert tf.read() == "<native>"
    finally:
        shutil.rmtree(t)

@responses.activate
def test_layer_set_xml(client):
    lv_url = client.get_url('VERSION', 'GET', 'single', {'layer_id': 1474, 'version_id': 4067})
    responses.add(responses.GET,
                  lv_url,
                  body=layers_version_single_good_simulated_response, status=200,
                  content_type='application/json')

    responses.add(responses.POST,
                  lv_url + 'metadata/',
                  body="", status=204,
                  adding_headers={"Location": lv_url + 'metadata/'})

    layer = client.layers.get_version(1474, 4067)

    old_meta = layer.metadata

    s = six.StringIO("<test>")
    layer.set_metadata(s)

    assert s.getvalue() == "<test>"

    # load layer, set metadata, reload layer
    assert len(responses.calls) == 3

    assert isinstance(responses.calls[1].request.body, six.StringIO)
    assert responses.calls[1].request.body.getvalue() == "<test>"

    assert isinstance(layer.metadata, Metadata)
    assert layer.metadata is not old_meta


@responses.activate
def test_layer_set_xml_manager(client):
    lv_url = client.get_url('VERSION', 'GET', 'single', {'layer_id': 1474, 'version_id': 4067})
    responses.add(responses.GET,
                  lv_url,
                  body=layers_version_single_good_simulated_response, status=200,
                  content_type='application/json')

    responses.add(responses.POST,
                  lv_url + 'metadata/',
                  body="", status=204,
                  adding_headers={"Location": lv_url + 'metadata/'})


    s = six.StringIO("<test>")
    r = client.layers.set_metadata(1474, 4067, s)

    assert len(responses.calls) == 1

    assert isinstance(responses.calls[0].request.body, six.StringIO)
    assert responses.calls[0].request.body.getvalue() == "<test>"

    assert r is None

