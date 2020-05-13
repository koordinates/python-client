import json

import pytest
import responses

from koordinates import Set, Client, Group


from .response_data.responses_3 import (
    sets_single_good_simulated_response,
    sets_new_draft_good_simulated_response,
    sets_single_draft_good_simulated_response,
)
from .response_data.responses_4 import sets_multiple_good_simulated_response


@pytest.fixture
def client():
    return Client("test.koordinates.com", token="test")


@responses.activate
def test_get_set_by_id(client):
    the_response = sets_single_good_simulated_response

    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "single", {"id": 1474}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    obj = client.sets.get(1474)
    assert isinstance(obj, Set)

    assert obj.title == "Ultra Fast Broadband Initiative Coverage"
    assert obj.group.name == "New Zealand Broadband Map"
    assert (
        obj.url_html
        == "https://test.koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/"
    )


@responses.activate
def test_get_set_set_returns_all_rows(client):
    the_response = sets_multiple_good_simulated_response

    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "multi"),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_sets_returned = 0

    for layer in client.sets.list():
        cnt_of_sets_returned += 1

    assert cnt_of_sets_returned == 2


@responses.activate
def test_set_create(client):
    responses.add(
        responses.POST,
        client.get_url("SET", "POST", "create"),
        body=sets_single_good_simulated_response,
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/sets/933/"
        },
    )

    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "single", {"id": 933}),
        body=sets_single_good_simulated_response,
        status=200,
    )

    s = Set()
    s.title = "test title"
    s.description = "description"
    s.group = 141
    s.items = [
        "https://test.koordinates.com/services/api/v1/layers/4226/",
        "https://test.koordinates.com/services/api/v1/layers/4228/",
        "https://test.koordinates.com/services/api/v1/layers/4227/",
        "https://test.koordinates.com/services/api/v1/layers/4061/",
        "https://test.koordinates.com/services/api/v1/layers/4147/",
        "https://test.koordinates.com/services/api/v1/layers/4148/",
    ]

    rs = client.sets.create(s)
    assert rs is s
    assert isinstance(s.group, Group)
    assert s.group.id == 141

    assert len(responses.calls) == 2

    req = json.loads(responses.calls[0].request.body.decode("utf-8"))
    assert len(req["items"]) == 6
    assert req["group"] == 141


@responses.activate
def test_set_list_drafts(client):
    # create a set, then check that it returns as a draft

    responses.add(
        responses.POST,
        client.get_url("SET", "POST", "create"),
        body=sets_new_draft_good_simulated_response,
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/sets/1/"
        },
    )

    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "single", {"id": 1}),
        body=sets_new_draft_good_simulated_response,
        status=200,
    )

    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "multidraft"),
        body=sets_single_draft_good_simulated_response,
        status=200,
    )

    s = Set()
    s.title = "test title"
    s.description = "description"
    s.group = 141
    s.items = [
        "https://test.koordinates.com/services/api/v1/layers/2/",
        "https://test.koordinates.com/services/api/v1/layers/1/",
    ]

    rs = client.sets.create(s)

    sets_amount = 0
    for _set in client.sets.list_drafts():
        sets_amount += 1

    assert sets_amount == 1

    assert rs is s
    assert rs.publish_to_catalog_services == False
    assert isinstance(s.group, Group)
    assert len(responses.calls) == 3
