import io
import os
import shutil
import tempfile

import pytest
import responses

from koordinates import Client, Metadata

from .response_data.responses_5 import layers_version_single_good_simulated_response
from .response_data.metadata import layers_version_metadata_post_response


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@responses.activate
def test_existing(client):
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
        body="<dc>",
        status=200,
        content_type="text/xml",
    )
    responses.add(
        responses.GET,
        "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
        body="<native>",
        status=200,
        content_type="text/xml",
    )

    layer = client.layers.get(1474)

    assert isinstance(layer.metadata, Metadata)
    assert (
        layer.metadata.dc
        == "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/"
    )
    assert set(layer.metadata.get_formats()) == {"iso", "dc"}
    assert layer.metadata._is_bound


@responses.activate
def test_get_xml(client):
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/",
        body="<dc>",
        status=200,
        content_type="text/xml",
    )
    responses.add(
        responses.GET,
        "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
        body="<native>",
        status=200,
        content_type="text/xml",
    )
    responses.add(
        responses.GET,
        "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/",
        body="<native>",
        status=200,
        content_type="text/xml",
    )

    layer = client.layers.get(1474)

    s = io.BytesIO()
    layer.metadata.get_xml(s, layer.metadata.FORMAT_DC)
    assert s.getvalue().decode("utf-8") == "<dc>"

    s = io.BytesIO()
    layer.metadata.get_xml(s, layer.metadata.FORMAT_NATIVE)
    assert s.getvalue().decode("utf-8") == "<native>"

    t = tempfile.mkdtemp()
    try:
        tfn = os.path.join(t, "metadata.xml")
        layer.metadata.get_xml(tfn)

        with open(tfn, "r") as tf:
            assert tf.read() == "<native>"
    finally:
        shutil.rmtree(t)


@responses.activate
def test_layer_set_xml(client):
    lv_url = client.get_url(
        "LAYER_VERSION", "GET", "single", {"layer_id": 1474, "version_id": 4067}
    )
    responses.add(
        responses.GET,
        lv_url,
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.POST,
        lv_url + "metadata/",
        body=layers_version_metadata_post_response,
        status=200,
        adding_headers={"Location": lv_url + "metadata/"},
    )

    layer = client.layers.get_version(1474, 4067)

    old_meta = layer.metadata

    s = io.StringIO("<test>")
    layer.set_metadata(s)

    assert s.getvalue() == "<test>"

    # load layer, set metadata, reload layer
    assert len(responses.calls) == 3

    assert isinstance(responses.calls[1].request.body, io.StringIO)
    assert responses.calls[1].request.body.getvalue() == "<test>"

    assert isinstance(layer.metadata, Metadata)
    assert layer.metadata is not old_meta


@responses.activate
def test_layer_set_xml_manager(client):
    lv_url = client.get_url(
        "LAYER_VERSION", "GET", "single", {"layer_id": 1474, "version_id": 4067}
    )
    responses.add(
        responses.GET,
        lv_url,
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.POST,
        lv_url + "metadata/",
        body=layers_version_metadata_post_response,
        status=200,
        adding_headers={"Location": lv_url + "metadata/"},
    )

    s = io.StringIO("<test>")
    r = client.layers.set_metadata(1474, 4067, s)

    assert len(responses.calls) == 1

    assert isinstance(responses.calls[0].request.body, io.StringIO)
    assert responses.calls[0].request.body.getvalue() == "<test>"
    assert responses.calls[0].request.headers == {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": client._user_agent,
        "Content-Type": "text/xml",
        "Authorization": "key test",
        "Connection": "keep-alive",
        "Content-Length": "6",
    }

    assert r is None
