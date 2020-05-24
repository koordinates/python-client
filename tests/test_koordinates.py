#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General tests.
"""


import urllib

import pytest
import responses

import koordinates
from koordinates import exceptions
from koordinates import Client
from koordinates import layers

from .response_data.responses_1 import layers_multiple_good_simulated_response
from .response_data.responses_2 import layers_single_good_simulated_response
from .response_data.responses_8 import layer_create_good_simulated_response
from .response_data.responses_9 import single_layer_all_versions_good_response
from .response_data.responses_9 import good_multi_layers_drafts_response


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@pytest.fixture
def test_client():
    return Client(token="test", host="test.koordinates.com")


@pytest.fixture
def bad_client():
    return Client(token="bad", host="koordinates.com")


def contains_substring(strtosearch, strtosearchfor):
    return strtosearch.lower().find(strtosearchfor) > -1


def test_instantiate_group_class():
    g = koordinates.Group(
        id=99, url="http//example.com", name="Group Name", country="NZ"
    )
    assert g.id == 99
    assert contains_substring(g.url, "example")
    assert g.name == "Group Name"
    assert g.country == "NZ"


def test_instantiate_data_class():
    d = layers.LayerData(encoding=None, crs="EPSG:2193", geometry_field="GEOMETRY")
    assert d.encoding == None
    assert d.crs == "EPSG:2193"
    assert d.geometry_field == "GEOMETRY"


@pytest.mark.skip("FIXME")
def test_instantiate_field_class():
    f = koordinates.Field("Field Name", "integer")
    assert f.name == "Field Name"
    assert f.type == "integer"


@responses.activate
def test_get_layerset_bad_auth_check_status(bad_client):
    the_response = """{"detail": "Authentication credentials were not provided."}"""

    responses.add(
        responses.GET,
        bad_client.get_url("LAYER", "GET", "multi"),
        body=the_response,
        status=401,
        content_type="application/json",
    )

    with pytest.raises(exceptions.AuthenticationError):
        for layer in bad_client.layers.list():
            pass


@responses.activate
def test_create_layer(client):
    the_response = layer_create_good_simulated_response

    responses.add(
        responses.POST,
        client.get_url("LAYER", "POST", "create"),
        body=the_response,
        status=201,
        content_type="application/json",
    )

    obj_lyr = koordinates.Layer()
    obj_lyr.name = "A Test Layer Name for Unit Testing"

    obj_lyr.group = 263
    obj_lyr.data = layers.LayerData(datasources=[144355])

    result_layer = client.layers.create(obj_lyr)
    assert result_layer is obj_lyr
    assert obj_lyr.created_at.year == 2015
    assert obj_lyr.created_at.month == 6
    assert obj_lyr.created_at.day == 11
    assert obj_lyr.created_at.hour == 11
    assert obj_lyr.created_at.minute == 14
    assert obj_lyr.created_at.second == 10
    assert obj_lyr.created_by == 18504

    # FIXME: API should return a full response
    # assert obj_lyr.group.id == 263
    # assert obj_lyr.group.url == "https://test.koordinates.com/services/api/v1/groups/{}/".format(obj_lyr.group.id)
    # assert obj_lyr.group.name == "Wellington City Council"
    # assert obj_lyr.group.country == "NZ"


@responses.activate
def test_get_layerset_bad_auth_check_exception(bad_client):
    the_response = """{"detail": "Authentication credentials were not provided."}"""

    responses.add(
        responses.GET,
        bad_client.get_url("LAYER", "GET", "multi"),
        body=the_response,
        status=401,
        content_type="application/json",
    )

    with pytest.raises(exceptions.AuthenticationError):
        for layer in bad_client.layers.list():
            pass


@responses.activate
def test_get_layerset_returns_all_rows(client):
    the_response = layers_multiple_good_simulated_response

    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "multi"),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_layers_returned = 0

    for layer in client.layers.list():
        cnt_of_layers_returned += 1

    assert cnt_of_layers_returned == 100


@responses.activate
def test_get_draft_layerset_returns_all_rows(client):
    the_response = good_multi_layers_drafts_response

    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "multidraft"),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_draft_layers_returned = 0

    for layer in client.layers.list_drafts():
        cnt_of_draft_layers_returned += 1

    assert cnt_of_draft_layers_returned == 12


@responses.activate
def test_get_draft_layerset_test_characteristics_of_response(client):
    the_response = good_multi_layers_drafts_response

    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "multidraft"),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_draft_layers_returned = 0

    # import pdb;pdb.set_trace()
    for layer in client.layers.list_drafts():
        if cnt_of_draft_layers_returned == 0:
            assert layer.id == 7955
            assert layer.name == "Built-Up Area"
            assert layer.first_published_at.year == 2015
            assert layer.first_published_at.month == 4
            assert layer.first_published_at.day == 21
            assert layer.first_published_at.hour == 0
            assert layer.first_published_at.minute == 59
            assert layer.first_published_at.second == 55
        if cnt_of_draft_layers_returned == 11:
            assert layer.id == 8113
            assert layer.name == "shea-test-layer-14"
        cnt_of_draft_layers_returned += 1


# This test is now impossible to conduct with the change in the way the
# the URL templates are populated - part of which is that the hostname
# is picked up at a higher level than previously. I'm putting this one
# on ice until other things have stablilised at which point changes should
# be made sufficient to allow this test or one of corresponding capability
#   @responses.activate
#   def test_get_layerset_with_non_default_host(client):

#       filter_value = str(uuid.uuid1())
#       test_domain = str(uuid.uuid1()).replace("-", "")
#       order_by_key = 'name'
#       test_host_name = "{fakedomain}.com".format(fakedomain=test_domain)
#       clientalthost = Client('test', test_host_name)

#       clientalthost.layer.get_list().filter(filter_value).order_by(order_by_key)

#       parsedurl = urllib.parse.urlparse(clientalthost.layer.url)

#       assert contains_substring(parsedurl.hostname, test_host_name)
#       assert parsedurl.hostname == test_host_name


@responses.activate
def test_get_layerset_filter(client):
    q = client.layers.list().filter(kind="vector")
    parsedurl = urllib.parse.urlparse(q._to_url())
    assert contains_substring(parsedurl.query, "kind=vector")


@responses.activate
def test_get_layerset_sort(client):
    q = client.layers.list().order_by("name")
    parsedurl = urllib.parse.urlparse(q._to_url())
    assert contains_substring(parsedurl.query, "sort=name")


@responses.activate
def test_get_layer_with_timeout(client):

    the_response = "{}"
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=504,
        content_type="application/json",
    )

    with pytest.raises(exceptions.ServiceUnvailable):
        client.layers.get(1474)


@responses.activate
def test_get_layer_with_rate_limiting(client):

    the_response = "{}"
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=429,
        content_type="application/json",
    )

    with pytest.raises(exceptions.RateLimitExceeded):
        client.layers.get(1474)


@responses.activate
def test_layer_import(test_client):
    the_response = layers_single_good_simulated_response
    layer_id = 999
    version_id = 998
    responses.add(
        responses.POST,
        test_client.get_url(
            "LAYER_VERSION",
            "POST",
            "import",
            {"version_id": version_id, "layer_id": layer_id},
        ),
        body=the_response,
        status=202,
        content_type="application/json",
    )

    test_client.layers.start_import(layer_id, version_id)


@responses.activate
def test_layer_hierarchy_of_classes(client):
    the_response = layers_single_good_simulated_response
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    obj = client.layers.get(1474)
    assert obj.categories[0]["slug"] == "cadastral"
    assert obj.data.crs == "EPSG:2193"
    assert obj.data.fields[0]["type"] == "geometry"
    assert set(obj.tags) == {"building", "footprint", "outline", "structure"}


@responses.activate
def test_layer_date_conversion(client):

    the_response = layers_single_good_simulated_response
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    obj = client.layers.get(1474)
    assert obj.first_published_at.year == 2010
    assert obj.first_published_at.month == 6
    assert obj.first_published_at.day == 21
    assert obj.first_published_at.hour == 5
    assert obj.first_published_at.minute == 5
    assert obj.first_published_at.second == 5

    assert obj.collected_at[0].year == 1996
    assert obj.collected_at[0].month == 12
    assert obj.collected_at[0].day == 31

    assert obj.collected_at[1].year == 2012
    assert obj.collected_at[1].month == 5
    assert obj.collected_at[1].day == 1
    assert obj.collected_at[1].hour == 0
    assert obj.collected_at[1].minute == 0
    assert obj.collected_at[1].second == 0


@responses.activate
def test_get_layerset_bad_filter_and_sort(client):
    with pytest.raises(exceptions.ClientValidationError):
        client.layers.list().filter(bad_attribute=True)


@responses.activate
def test_get_layerset_bad_sort(client):
    with pytest.raises(exceptions.ClientValidationError):
        client.layers.list().order_by("bad_attribute")


@responses.activate
def test_get_layer_by_id_bad_auth(bad_client):
    the_response = """{"detail": "Authentication credentials were not provided."}"""

    responses.add(
        responses.GET,
        bad_client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=401,
        content_type="application/json",
    )

    try:
        bad_client.layers.get(1474)
    except Exception:
        pass

    with pytest.raises(exceptions.AuthenticationError):
        bad_client.layers.get(1474)


@responses.activate
def test_get_layer_by_id(client):

    the_response = layers_single_good_simulated_response

    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    obj = client.layers.get(1474)

    assert obj.name == "Wellington City Building Footprints"


@responses.activate
def test_get_all_layer_version_by_layer_id(client):
    the_response = single_layer_all_versions_good_response

    responses.add(
        responses.GET,
        client.get_url("LAYER_VERSION", "GET", "multi", {"layer_id": 1474}),
        body=the_response,
        status=200,
        content_type="application/json",
    )

    cnt_of_versions_returned = 0

    for version in client.layers.list_versions(layer_id=1474):
        cnt_of_versions_returned += 1

    assert cnt_of_versions_returned == 2

    assert version.id == 32
    assert version.status == "ok"
    assert version.created_by == 2879
