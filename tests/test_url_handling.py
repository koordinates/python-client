# -*- coding: utf-8 -*-


import pytest

from koordinates import Client


@pytest.fixture
def client():
    return Client("koordinates.com", "test")


@pytest.fixture
def testclient():
    return Client("test.koordinates.com", "test")


def test_sets_url(client):
    assert (
        client.get_url("SET", "GET", "single", {"id": 999})
        == "https://koordinates.com/services/api/v1/sets/999/"
    )


def test_sets_domain_url(testclient):
    assert (
        testclient.get_url("SET", "GET", "single", {"id": 999})
        == "https://test.koordinates.com/services/api/v1/sets/999/"
    )


def test_sets_multi_url(client):
    assert (
        client.get_url("SET", "GET", "multi")
        == "https://koordinates.com/services/api/v1/sets/"
    )


def test_layers_url(client):
    assert (
        client.get_url("LAYER", "GET", "single", {"id": 999})
        == "https://koordinates.com/services/api/v1/layers/999/"
    )


def test_layers_multi_url(client):
    assert (
        client.get_url("LAYER", "GET", "multi")
        == "https://koordinates.com/services/api/v1/layers/"
    )


def test_layer_versions_url(client):
    assert (
        client.get_url(
            "LAYER_VERSION", "GET", "single", {"layer_id": 1494, "version_id": 4067}
        )
        == "https://koordinates.com/services/api/v1/layers/1494/versions/4067/"
    )


def test_layer_versions_multi_url(client):
    assert (
        client.get_url("LAYER_VERSION", "GET", "multi", {"layer_id": 1494})
        == "https://koordinates.com/services/api/v1/layers/1494/versions/"
    )
