import pytest
import responses

from koordinates import Client, License, ClientValidationError

from .response_data.licenses import license_list, license_cc_10
from .response_data.responses_5 import layers_version_single_good_simulated_response


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@responses.activate
def test_list(client):
    responses.add(
        responses.GET,
        client.get_url("LICENSE", "GET", "multi"),
        body=license_list,
        status=200,
        content_type="application/json",
    )

    licenses = list(client.licenses.list())

    assert len(licenses) == 23
    assert len(responses.calls) == 1


@responses.activate
def test_list_cc(client):
    responses.add(
        responses.GET,
        client.get_url(
            "LICENSE", "GET", "cc", {"slug": "cc-by-nc", "jurisdiction": ""}
        ),
        body=license_cc_10,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        client.get_url(
            "LICENSE", "GET", "cc", {"slug": "cc-by-nc", "jurisdiction": "au"}
        ),
        body=license_cc_10,
        status=200,
        content_type="application/json",
    )

    license = client.licenses.get_creative_commons("cc-by-nc")
    assert isinstance(license, License)
    license = client.licenses.get_creative_commons("cc-by-nc", "au")
    assert isinstance(license, License)

    with pytest.raises(ClientValidationError):
        client.licenses.get_creative_commons("nc", "au")

    assert len(responses.calls) == 2


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        client.get_url("LICENSE", "GET", "single", {"id": 10}),
        body=license_cc_10,
        status=200,
        content_type="application/json",
    )

    license = client.licenses.get(10)
    assert isinstance(license, License)
    assert license.id == 10
    assert license.type == "cc-by-nd"
    assert license.jurisdiction == "nz"

    assert (
        str(license)
        == "10 - Creative Commons Attribution-No Derivative Works 3.0 New Zealand"
    )


@responses.activate
def test_layer(client):
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    layer = client.layers.get(1474)
    assert isinstance(layer.license, License)

    license = layer.license
    assert license.id == 9
