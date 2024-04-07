#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_publish
----------------------------------

Tests for the `koordinates.publishing` module.
"""


import pytest
import responses

# from koordinates import api
from koordinates import exceptions
from koordinates import Client, Publish

from .response_data.responses_5 import layers_version_single_good_simulated_response
from .response_data.responses_7 import publish_single_good_simulated_response
from .response_data.responses_7 import publish_multiple_get_simulated_response


@pytest.fixture
def client():
    return Client(token="test", host="koordinates.com")


@pytest.fixture
def testclient():
    return Client(token="test", host="test.koordinates.com")


@responses.activate
def test_publish_get_by_id(client):
    the_response = publish_single_good_simulated_response

    publish_id = 2054
    responses.add(
        responses.GET,
        client.get_url("PUBLISH", "GET", "single", {"id": publish_id}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    obj = client.publishing.get(publish_id)

    assert obj.state == "completed"
    assert obj.created_by.id == 18504
    assert len(obj.items) == 1
    assert (
        obj.items[0]
        == "https://test.koordinates.com/services/api/v1/layers/8092/versions/9822/"
    )
    assert obj.created_at.year == 2015
    assert obj.created_at.month == 6
    assert obj.created_at.day == 8
    assert obj.created_at.hour == 3
    assert obj.created_at.minute == 40
    assert obj.created_at.second == 40
    assert obj.created_by.id == 18504


@responses.activate
def test_publish_get_all_rows(client):
    the_response = publish_multiple_get_simulated_response

    responses.add(
        responses.GET,
        client.get_url("PUBLISH", "GET", "multi"),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_publish_records_returned = 0

    for pub_record in client.publishing.list():
        if cnt_of_publish_records_returned == 0:
            assert pub_record.id == 2054
            assert pub_record.error_strategy == "abort"
        cnt_of_publish_records_returned += 1

    assert cnt_of_publish_records_returned == 7


@pytest.mark.skip("FIXME")
@responses.activate
def test_multipublish_resource_specification(testclient):
    the_response = """{}"""
    responses.add(
        responses.POST,
        testclient.get_url("PUBLISH", "POST", "create"),
        body=the_response,
        status=400, # because items below can't be resolved
        content_type="application/json",
    )

    pr = Publish()
    pr.items = [
        "https://test.koordinates.com/services/api/v1/layers/100/versions/1000/",
        "https://test.koordinates.com/services/api/v1/layers/101/versions/1001/",
        "https://test.koordinates.com/services/api/v1/layers/102/versions/1002/",
        "https://test.koordinates.com/services/api/v1/tables/200/versions/2000/",
        "https://test.koordinates.com/services/api/v1/tables/201/versions/2001/",
        "https://test.koordinates.com/services/api/v1/tables/202/versions/2002/",
    ]

    with pytest.raises(exceptions.ServerError):
        # the Responses mocking will result in a 999 being returned
        testclient.publishing.create(pr)


@pytest.mark.skip("FIXME")
@responses.activate
def test_multipublish_bad_args(testclient):
    the_response = """{}"""

    responses.add(
        responses.POST,
        testclient.get_url("PUBLISH", "POST", "create"),
        body=the_response,
        status=400,
        content_type="application/json",
    )

    pr = Publish()
    with pytest.raises(exceptions.ServerError):
        testclient.publishing.create(pr)

    pr = Publish(publish_strategy=Publish.PUBLISH_STRATEGY_TOGETHER)
    with pytest.raises(exceptions.ServerError):
        testclient.publishing.create(pr)

    pr = Publish(
        publish_strategy=Publish.PUBLISH_STRATEGY_TOGETHER,
        error_strategy=Publish.ERROR_STRATEGY_ABORT,
    )
    with pytest.raises(exceptions.ServerError):
        # the Responses mocking will result in a 999 being returned
        testclient.publishing.create(pr)


@responses.activate
def test_publish_single_layer_version(client):
    the_response = layers_version_single_good_simulated_response
    responses.add(
        responses.GET,
        client.get_url(
            "LAYER_VERSION", "GET", "single", {"layer_id": 1474, "version_id": 4067}
        ),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    lv = client.layers.get_version(1474, 4067)

    assert lv.id == 1474
    assert lv.version.id == 4067

    the_response = """{"id": 2057, "url": "https://test.koordinates.com/services/api/v1/publish/2057/", "state": "publishing", "created_at": "2015-06-08T10:39:44.823Z", "created_by": {"id": 18504, "url": "https://test.koordinates.com/services/api/v1/users/18504/", "first_name": "Richard", "last_name": "Shea", "country": "NZ"}, "error_strategy": "abort", "publish_strategy": "together", "publish_at": null, "items": ["https://test.koordinates.com/services/api/v1/layers/1474/versions/4067/"]}"""
    publish_url = "https://test.koordinates.com/services/api/v1/publish/2057/"

    responses.add(
        responses.POST,
        client.get_url(
            "LAYER_VERSION", "POST", "publish", {"layer_id": 1474, "version_id": 4067}
        ),
        body="",
        status=201,
        adding_headers={"Location": publish_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        publish_url,
        body=the_response,
        status=200,
        content_type="application/json",
    )

    p = lv.publish()
    assert isinstance(p, Publish)
    assert p.id == 2057


@responses.activate
def test_cancel(client):
    publish_id = 2054

    responses.add(
        responses.GET,
        client.get_url("PUBLISH", "GET", "single", {"id": publish_id}),
        body=publish_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.DELETE,
        client.get_url("PUBLISH", "DELETE", "single", {"id": publish_id}),
        body="",
        status=204,
        content_type="application/json",
    )

    obj = client.publishing.get(publish_id)
    obj.cancel()
