# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.catalog` module.
"""


import contextlib
import json
import os
import re
import logging

import pytest
import responses

from koordinates import Client, BadRequest


def _env_set(key, value):
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


@contextlib.contextmanager
def env_override(key, value):
    """
    Contextmanager. Temporarily override an environment variable.
    """
    orig = os.environ.get(key)
    _env_set(key, value)
    try:
        yield
    finally:
        # Put it back the way it was
        _env_set(key, orig)


@pytest.fixture
def client():
    return Client(host="test.koordinates.com", token="12345abcde")


def test_token_from_env():
    with env_override("KOORDINATES_TOKEN", None):
        with pytest.raises(KeyError):
            Client(host="test.koordinates.com")

    with env_override("KOORDINATES_TOKEN", "abcde12345"):
        client = Client(host="test.koordinates.com")
        assert client.token == "abcde12345"


def test_token_from_param():
    with env_override("KOORDINATES_TOKEN", None):
        client = Client(host="test.koordinates.com", token="12345abcde")
        assert client.token == "12345abcde"

    with env_override("KOORDINATES_TOKEN", "don't use me"):
        client = Client(host="test.koordinates.com", token="12345abcde")
        assert client.token == "12345abcde"


@pytest.mark.parametrize(
    "api_version",
    [
        pytest.param(None, id="api_version_default"),
        pytest.param("v2", id="api_version=v2"),
    ],
)
def test_get_url_path(client, api_version):
    assert "/layers/" == client.get_url_path("LAYER", "GET", "multi")
    assert "/publish/12345/" == client.get_url_path(
        "PUBLISH", "DELETE", "single", {"id": 12345}
    )


def test_get_url(client):
    url = client.get_url("LAYER", "GET", "multi")
    assert url == "https://test.koordinates.com/services/api/v1/layers/"

    url = client.get_url("PUBLISH", "DELETE", "single", {"id": 12345})
    assert url == "https://test.koordinates.com/services/api/v1/publish/12345/"


def test_reverse_url(client):
    params = client.reverse_url(
        "LAYER", "https://test.koordinates.com/services/api/v1/layers/12345/"
    )
    assert params == {"id": "12345"}

    params = client.reverse_url(
        "LAYER_VERSION",
        "https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/",
    )
    assert params == {"layer_id": "12345", "version_id": "3456"}

    params = client.reverse_url(
        "LAYER_VERSION",
        "https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/publish/",
        verb="POST",
        urltype="publish",
    )
    assert params == {"layer_id": "12345", "version_id": "3456"}

    params = client.reverse_url(
        "LICENSE",
        "https://test.koordinates.com/services/api/v1/licenses/cc-by/nz/",
        verb="GET",
        urltype="cc",
    )
    assert params == {"slug": "cc-by", "jurisdiction": "nz"}

    with pytest.raises(KeyError):
        client.reverse_url("LAYER_VERSION", "")
    with pytest.raises(KeyError):
        client.reverse_url(
            "LAYER_VERSION",
            "https://test.koordinates.com/services/api/v1/layers/12345/",
        )
    with pytest.raises(KeyError):
        client.reverse_url("LAYER_VERSION", None)
    with pytest.raises(KeyError):
        client.reverse_url("LAYER_VERSION", "/layers/12345/versions/3456/")


@responses.activate
def test_user_agent(client):
    responses.add(
        responses.GET,
        "https://test.koordinates.com/api/v1/test/",
        body="[]",
        status=200,
        content_type="application/json",
    )

    r = client.request("GET", "https://test.koordinates.com/api/v1/test/")
    r.raise_for_status()

    req = responses.calls[0].request
    ua = req.headers.get("User-Agent")
    assert ua.startswith("KoordinatesPython/")


@responses.activate
def test_server_error(client):

    # Form / field errors:
    responses.add(
        responses.POST,
        "https://test.koordinates.com/api/v1/layers/123/versions/",
        body='{"autoupdate_schedule":["This field is required when autoupdate is on."]}',
        status=400,
        content_type="application/json",
    )

    with pytest.raises(BadRequest) as cm:
        client.request(
            "POST", "https://test.koordinates.com/api/v1/layers/123/versions/", json={}
        )

    e = cm.value
    assert (
        str(e) == "autoupdate_schedule: This field is required when autoupdate is on."
    )
    assert (
        repr(e)
        == "BadRequest('autoupdate_schedule: This field is required when autoupdate is on.')"
    )

    responses.add(
        responses.POST,
        "https://test.koordinates.com/api/v1/layers/1234/versions/",
        body='{"autoupdate_schedule":["This field is required when autoupdate is on."], "number":["Value must be >10", "Value must be <100"]}',
        status=400,
        content_type="application/json",
    )

    with pytest.raises(BadRequest) as cm:
        client.request(
            "POST", "https://test.koordinates.com/api/v1/layers/1234/versions/", json={}
        )

    e = cm.value
    estr = set(str(e).split("\n"))
    assert estr == {
        "number: Value must be >10; Value must be <100",
        "autoupdate_schedule: This field is required when autoupdate is on.",
    }
    assert repr(e) == "BadRequest('%s')" % str(e)

    # Other detail errors:
    responses.add(
        responses.POST,
        "https://test.koordinates.com/api/v1/layers/123/versions/123/import/",
        body='{"detail": "No valid datasources to import"}',
        status=400,
        content_type="application/json",
    )
    with pytest.raises(BadRequest) as cm:
        client.request(
            "POST",
            "https://test.koordinates.com/api/v1/layers/123/versions/123/import/",
        )

    e = cm.value
    assert str(e) == "detail: No valid datasources to import"
    assert repr(e) == "BadRequest('detail: No valid datasources to import')"


@responses.activate
def test_request_logging(caplog, client):
    caplog.set_level(logging.DEBUG)

    responses.add(
        responses.GET,
        "https://test.koordinates.com/api/v1/test/",
        body="[]",
        status=200,
        content_type="application/json",
    )

    r = client.request(
        "GET",
        "https://test.koordinates.com/api/v1/test/",
        json={"some": ["data", 1]},
        headers={"FooHeader": "Bar"},
    )
    r.raise_for_status()

    lreq = caplog.records[0]
    lmsg = lreq.getMessage()
    assert lmsg.startswith("Request: ")

    lf = re.match(
        "^Request: GET https://test.koordinates.com/api/v1/test/ headers=(?P<headers>.*) body=(?P<body>.*)$",
        lmsg,
    )

    lbody = json.loads(lf.group("body"))
    assert lbody == {"some": ["data", 1]}

    lheaders = json.loads(lf.group("headers"))
    assert "FooHeader" in lheaders
    assert "Authorization" not in lheaders


def test_get_url_specified_url_version(client):
    url_version = "v1.x"
    layer_id = "12345"
    client.url_version = url_version
    url = client.get_url("PUBLISH", "DELETE", "single", {"id": layer_id})
    expected_url = "https://test.koordinates.com/services/api/{url_version}/publish/{layer_id}/".format(
        url_version=url_version, layer_id=layer_id
    )
    assert url == expected_url


def test_reverse_url_specified_url_version(client):
    url_version = "v1.x"
    layer_id = "12345"
    client.url_version = url_version
    url = client.get_url("PUBLISH", "DELETE", "single", {"id": layer_id})
    params = client.reverse_url(datatype="PUBLISH", url=url, verb="DELETE")
    expected_params = {"id": layer_id}
    assert params == expected_params


def test_invalid_api_version_error(client):
    invalid_api_version = "v2"
    client.api_version = invalid_api_version
    expected_error_msg = "'{version}' is not a valid `api_version`.".format(
        version=invalid_api_version
    )
    with pytest.raises(ValueError, match=expected_error_msg):
        client.get_url("PUBLISH", "DELETE", "single", {"id": 12345})
