import pytest

from koordinates import Permission
from koordinates import Client, Group, User

from .response_data.responses_10 import (
    layer_list_permissions_good_simulated_response,
    layer_permission_simulated_response,
)
from .response_data.responses_10 import (
    set_permission_simulated_response,
    set_list_permissions_good_simulated_response,
)
from .response_data.responses_10 import (
    source_permission_simulated_response,
    source_list_permissions_good_simulated_response,
)
from .response_data.sources import source_detail
from .response_data.responses_5 import layers_version_single_good_simulated_response
from .response_data.responses_3 import sets_single_good_simulated_response


# FIXTURES


@pytest.fixture
def responses():
    import responses

    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@pytest.fixture
def layer(responses, client):
    responses.add(
        responses.GET,
        client.get_url("LAYER", "GET", "single", {"id": 1474}),
        body=layers_version_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    yield client.layers.get(1474)


@pytest.fixture
def set_(responses, client):
    responses.add(
        responses.GET,
        client.get_url("SET", "GET", "single", {"id": 933}),
        body=sets_single_good_simulated_response,
        status=200,
        content_type="application/json",
    )
    yield client.sets.get(933)


@pytest.fixture
def source(responses, client):
    responses.add(
        responses.GET,
        client.get_url("SOURCE", "GET", "single", {"id": 21836}),
        body=source_detail,
        status=200,
        content_type="application/json",
    )
    yield client.sources.get(21836)


# TESTS


def test_list_layer_permissions(responses, client, layer):
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")
    responses.add(
        responses.GET,
        target_url,
        body=layer_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    cnt_permissions_returned = 0
    for obj in layer.permissions.list():
        assert isinstance(obj, Permission)
        assert isinstance(obj.group, Group)
        assert obj.permission == "download"
        assert obj.id == "group.everyone"
        assert obj.group.id == 4
        assert obj.group.name == "Everyone"
        assert obj.group.url == "https://test.koordinates.com/services/api/v1/groups/4/"
        cnt_permissions_returned += 1

    assert cnt_permissions_returned == 1


def test_create_layer_permission(responses, client, layer):
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path("PERMISSION", "POST", "single")
    responses.add(
        responses.POST,
        target_url,
        body=layer_permission_simulated_response,
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/layers/%s/permissions/%s/"
            % (layer.id, "108")
        },
    )
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 108}
    )
    responses.add(
        responses.GET, target_url, body=layer_permission_simulated_response, status=200
    )
    permission = Permission()
    permission.group = "108"
    permission.permission = "download"
    response = layer.permissions.create(permission)

    assert response.id == permission.id
    assert response.permission == permission.permission
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 108 == permission.group.id


def test_set_layer_permissions(responses, client, layer):
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path("PERMISSION", "PUT", "multi")
    responses.add(
        responses.PUT,
        target_url,
        body=layer_list_permissions_good_simulated_response,
        status=200,
    )
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")
    responses.add(
        responses.GET,
        target_url,
        body=layer_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    data = [{"permission": "download", "group": "everyone"}]

    for obj in layer.permissions.set(data):
        assert isinstance(obj, Permission)
        assert isinstance(obj.group, Group)
        assert obj.permission == "download"
        assert obj.id == "group.everyone"


def test_get_layer_permission(responses, client, layer):
    base_url = client.get_url("LAYER", "GET", "single", {"id": layer.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 108}
    )
    responses.add(
        responses.GET, target_url, body=layer_permission_simulated_response, status=200
    )

    response = layer.permissions.get(108)

    assert response.id == "group.108"
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 108 == response.group.id


def test_list_set_permissions(responses, client, set_):
    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")

    responses.add(
        responses.GET,
        target_url,
        body=set_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    cnt_permissions_returned = 0
    for obj in set_.permissions.list():
        assert isinstance(obj, Permission)
        assert obj.permission in ["admin", "view"]
        if obj.group:
            assert isinstance(obj.group, Group)
            assert (
                obj.group.url
                == "https://test.koordinates.com/services/api/v1/groups/%s/"
                % obj.group.id
            )
        elif obj.user:
            assert isinstance(obj.user, User)
            assert (
                obj.user.url
                == "https://test.koordinates.com/services/api/v1/users/%s/"
                % obj.user.id
            )
        cnt_permissions_returned += 1

    assert cnt_permissions_returned == 3


def test_create_set_permission(responses, client, set_):
    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path("PERMISSION", "POST", "single")
    responses.add(
        responses.POST,
        target_url,
        body=set_permission_simulated_response,
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/sets/%s/permissions/%s/"
            % (set_.id, "34")
        },
    )

    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 34}
    )
    responses.add(
        responses.GET, target_url, body=set_permission_simulated_response, status=200
    )

    permission = Permission()
    permission.group = "34"
    permission.permission = "edit"
    response = set_.permissions.create(permission)

    assert response.id == permission.id
    assert response.permission == permission.permission
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 34 == permission.group.id


def test_set_set_permissions(responses, client, set_):
    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path("PERMISSION", "PUT", "multi")
    responses.add(
        responses.PUT,
        target_url,
        body=set_list_permissions_good_simulated_response,
        status=200,
    )
    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")
    responses.add(
        responses.GET,
        target_url,
        body=set_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    data = [
        {"permission": "admin", "user": "4"},
        {"permission": "admin", "group": "administrators"},
        {"permission": "view", "group": "everyone"},
    ]

    cnt_permissions_returned = 0
    for obj in set_.permissions.set(data):
        assert isinstance(obj, Permission)
        assert obj.permission in ["admin", "view"]
        if obj.group:
            assert isinstance(obj.group, Group)
            assert (
                obj.group.url
                == "https://test.koordinates.com/services/api/v1/groups/%s/"
                % obj.group.id
            )
        elif obj.user:
            assert isinstance(obj.user, User)
            assert (
                obj.user.url
                == "https://test.koordinates.com/services/api/v1/users/%s/"
                % obj.user.id
            )
        cnt_permissions_returned += 1

    assert cnt_permissions_returned == 3


def test_get_set_permission(responses, client, set_):
    base_url = client.get_url("SET", "GET", "single", {"id": set_.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 34}
    )
    responses.add(
        responses.GET, target_url, body=set_permission_simulated_response, status=200
    )

    response = set_.permissions.get(34)

    assert response.id == "group.34"
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 34 == response.group.id


def test_list_source_permissions(responses, client, source):
    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")

    responses.add(
        responses.GET,
        target_url,
        body=source_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    cnt_permissions_returned = 0
    for obj in source.permissions.list():
        assert isinstance(obj, Permission)
        assert obj.permission in ["admin", "view"]
        if obj.group:
            assert isinstance(obj.group, Group)
            assert (
                obj.group.url
                == "https://test.koordinates.com/services/api/v1/groups/%s/"
                % obj.group.id
            )
        elif obj.user:
            assert isinstance(obj.user, User)
            assert (
                obj.user.url
                == "https://test.koordinates.com/services/api/v1/users/%s/"
                % obj.user.id
            )
        cnt_permissions_returned += 1

    assert cnt_permissions_returned == 3


def test_create_source_permission(responses, client, source):
    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path("PERMISSION", "POST", "single")
    responses.add(
        responses.POST,
        target_url,
        body=source_permission_simulated_response,
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/sources/%s/permissions/%s/"
            % (source.id, "85")
        },
    )

    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 85}
    )
    responses.add(
        responses.GET, target_url, body=source_permission_simulated_response, status=200
    )

    permission = Permission()
    permission.group = "85"
    permission.permission = "download"
    response = source.permissions.create(permission)

    assert response.id == permission.id
    assert response.permission == permission.permission
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 85 == permission.group.id


def test_source_set_permissions(responses, client, source):
    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path("PERMISSION", "PUT", "multi")
    responses.add(
        responses.PUT,
        target_url,
        body=source_list_permissions_good_simulated_response,
        status=200,
    )
    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path("PERMISSION", "GET", "multi")
    responses.add(
        responses.GET,
        target_url,
        body=source_list_permissions_good_simulated_response,
        status=200,
        content_type="application/json",
    )

    data = [
        {"permission": "admin", "user": "4"},
        {"permission": "admin", "group": "administrators"},
        {"permission": "view", "group": "everyone"},
    ]

    cnt_permissions_returned = 0
    for obj in source.permissions.set(data):
        assert isinstance(obj, Permission)
        assert obj.permission in ["admin", "view"]
        if obj.group:
            assert isinstance(obj.group, Group)
            assert (
                obj.group.url
                == "https://test.koordinates.com/services/api/v1/groups/%s/"
                % obj.group.id
            )
        elif obj.user:
            assert isinstance(obj.user, User)
            assert (
                obj.user.url
                == "https://test.koordinates.com/services/api/v1/users/%s/"
                % obj.user.id
            )
        cnt_permissions_returned += 1

    assert cnt_permissions_returned == 3


def test_source_layer_permission(responses, client, source):
    base_url = client.get_url("SOURCE", "GET", "single", {"id": source.id})
    target_url = base_url + client.get_url_path(
        "PERMISSION", "GET", "single", {"permission_id": 85}
    )
    responses.add(
        responses.GET, target_url, body=source_permission_simulated_response, status=200
    )

    response = source.permissions.get(85)

    assert response.id == "group.85"
    assert isinstance(response, Permission)
    assert isinstance(response.group, Group)
    assert 85 == response.group.id
