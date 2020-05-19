# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.catalog` module.
"""


import pytest
import responses

from koordinates import Client, Table, Layer, Set
from koordinates.catalog import CatalogEntry

from .response_data.catalog import response_1


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@responses.activate
def test_result_classes(client):
    responses.add(
        responses.GET,
        client.get_url("CATALOG", "GET", "multi"),
        body=response_1,
        status=200,
        content_type="application/json",
    )

    results = list(client.catalog.list())
    assert len(results) == 14

    assert isinstance(results[0], Table)
    assert isinstance(results[2], Layer)
    # TODO: Document
    assert isinstance(results[7], dict)
    assert "/documents/" in results[7]["url"]
    assert isinstance(results[12], Set)


@responses.activate
def test_latest(client):
    responses.add(
        responses.GET,
        client.get_url("CATALOG", "GET", "latest"),
        body=response_1,
        status=200,
        content_type="application/json",
    )

    results = list(client.catalog.list_latest())
    assert len(results) == 14

    results = list(client.catalog.list_latest().filter(version__status="importing"))
    assert len(results) == 14


def test_nocreate():
    with pytest.raises(TypeError):
        CatalogEntry()


def test_no_get(client):
    with pytest.raises(NotImplementedError):
        client.catalog.get(1)
