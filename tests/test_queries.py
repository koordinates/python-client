import json

import pytest
import responses
from responses import matchers
from urllib.parse import parse_qs, urlparse

from koordinates import base, Client
from koordinates.exceptions import ClientValidationError

from .test_models import FooManager, FooModel


@pytest.fixture
def manager():
    c = Client(host="test.koordinates.com", token="test", activate_logging=True)
    return FooManager(c)


def test_list(manager):
    q = manager.list()
    assert isinstance(q, base.Query)
    assert q._manager is manager
    assert q._target_url == FooManager.TEST_LIST_URL


def test_to_url(manager):
    q = manager.list()
    assert q._to_url() == FooManager.TEST_LIST_URL


def test_order_by(manager):
    base_q = manager.list()

    q = base_q.order_by("-sortable")
    assert "sort=-sortable" in q._to_url()

    q = base_q.order_by("sortable")
    assert "sort=sortable" in q._to_url()

    # should replace the previous sort
    q = base_q.order_by("-sortable")
    assert "sort=-sortable" in q._to_url()
    assert "sort=sortable" not in q._to_url()


def test_order_by_invalid(manager):
    base_q = manager.list()
    pytest.raises(ClientValidationError, base_q.order_by, "invalid")


def test_order_by_custom(manager):
    base_q = manager.list_custom_attrs()
    pytest.raises(ClientValidationError, base_q.order_by, "sortable")
    base_q.order_by("custom")


def test_clone(manager):
    q0 = manager.list().filter(thing="bang")
    assert dict(q0._filters) == {"thing": ["bang"]}
    assert q0._order_by == None

    q1 = q0.order_by("sortable")
    assert q1._order_by == "sortable"
    assert q0._order_by == None

    q1 = q0.filter(other="bob", thing="fred")
    assert dict(q0._filters) == {"thing": ["bang"]}
    assert dict(q1._filters) == {"thing": ["bang", "fred"], "other": ["bob"]}


def test_filter(manager):
    base_q = manager.list()

    q = (
        base_q.filter(thing=1)
        .filter(thing=2)
        .filter(other="3", other__op=4)
        .filter(b1="b2")
    )

    assert dict(q._filters) == {
        "thing": [1, 2],
        "other": ["3"],
        "other.op": [4],
        "b1": ["b2"],
    }

    # serialize:
    url = q._to_url()
    params = parse_qs(urlparse(url).query, keep_blank_values=True)
    assert params == {
        "thing": ["1", "2"],
        "other": ["3"],
        "other.op": ["4"],
        "b1": ["b2"],
    }


def test_filter_invalid(manager):
    base_q = manager.list()
    pytest.raises(ClientValidationError, base_q.filter, invalid="test")


def test_filter_custom(manager):
    base_q = manager.list_custom_attrs()
    pytest.raises(ClientValidationError, base_q.filter, thing="test")
    base_q.filter(custom=12)


def test_extra(manager):
    base_q = manager.list().filter(thing="value")

    q = base_q.extra(some_key="some_value")
    assert "some_key=some_value" in q._to_url()

    q = base_q.extra(thing="something_extra")
    url = q._to_url()
    params = parse_qs(urlparse(url).query, keep_blank_values=True)
    assert params == {
        "thing": ["value", "something_extra"],
    }


def test_expand(manager):
    q0 = manager.list()
    assert "Expand" not in q0._to_headers()

    q1 = manager.list().expand()
    assert "Expand" in q1._to_headers()


@responses.activate
def test_count(manager):
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        body="{}",
        content_type="application/json",
        adding_headers={"X-Resource-Range": "0-10/28"},
    )

    q = manager.list()
    count = len(q)
    assert count == 28

    # Second hit shouldn't do another request
    count = len(q)
    assert count == 28

    assert len(responses.calls) == 1


@responses.activate
def test_pagination(manager):
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        body=json.dumps([{"id": id} for id in range(10)]),
        content_type="application/json",
        adding_headers={
            "X-Resource-Range": "0-10/28",
            "Link": '<%s?page=2>; rel="page-next"' % FooManager.TEST_LIST_URL,
        },
    )
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        match=[matchers.query_param_matcher({'page': '2'})],
        body=json.dumps([{"id": id} for id in range(10, 20)]),
        content_type="application/json",
        adding_headers={
            "X-Resource-Range": "10-20/28",
            "Link": '<%s?page=3>; rel="page-next"' % FooManager.TEST_LIST_URL,
        },
    )
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        match=[matchers.query_param_matcher({'page': '3'})],
        body=json.dumps([{"id": id} for id in range(20, 28)]),
        content_type="application/json",
        adding_headers={"X-Resource-Range": "20-28/28",},
    )

    q = manager.list()
    for i, o in enumerate(q):
        continue

    assert i == 27  # 0-index
    assert len(responses.calls) == 3

    # Second hit shouldn't do another request
    count = len(q)
    assert count == 28
    assert len(responses.calls) == 3


@responses.activate
def test_slicing(manager):
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        match=[matchers.query_param_matcher({})],
        body=json.dumps([{"id": id} for id in range(10)]),
        content_type="application/json",
        adding_headers={
            "X-Resource-Range": "0-10/28",
            "Link": '<%s?page=2>; rel="page-next"' % FooManager.TEST_LIST_URL,
        },
    )
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        match=[matchers.query_param_matcher({'page': '2'})],
        body=json.dumps([{"id": id} for id in range(10, 20)]),
        content_type="application/json",
        adding_headers={
            "X-Resource-Range": "10-20/28",
            "Link": '<%s?page=3>; rel="page-next"' % FooManager.TEST_LIST_URL,
        },
    )
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        match=[matchers.query_param_matcher({'page': '3'})],
        body=json.dumps([{"id": id} for id in range(20, 28)]),
        content_type="application/json",
        adding_headers={"X-Resource-Range": "20-28/28",},
    )

    q = manager.list()
    for i, o in enumerate(q[:3]):
        assert isinstance(o, FooModel)

    assert i == 2  # 0-index
    assert len(responses.calls) == 1

    # When the slice is bigger than the dataset
    for i, o in enumerate(q[:50]):
        continue

    assert i == 27  # 0-index
    assert len(responses.calls) == 4

    # query[0] slice
    assert q[0].id == 0
    assert q[3].id == 3
    pytest.raises(IndexError, lambda qq: qq[999], q)

    # Bad slices, we only support query[:N] where N>0
    pytest.raises(ValueError, lambda qq: qq[-1], q)
    pytest.raises(ValueError, lambda qq: qq[0:10], q)
    pytest.raises(ValueError, lambda qq: qq[10:20], q)
    pytest.raises(ValueError, lambda qq: qq[:10:3], q)
    pytest.raises(ValueError, lambda qq: qq[:-5], q)
    pytest.raises(ValueError, lambda qq: qq[:0], q)
    pytest.raises(ValueError, lambda qq: qq[1:30:2], q)


@responses.activate
def test_list_cast(manager):
    # Test that ``list(query)`` doesn't make an extra HEAD request
    responses.add(
        responses.HEAD,
        FooManager.TEST_LIST_URL,
        body="",
        content_type="application/json",
        adding_headers={"X-Resource-Range": "0-10/10",},
    )
    responses.add(
        responses.GET,
        FooManager.TEST_LIST_URL,
        body=json.dumps([{"id": id} for id in range(10)]),
        content_type="application/json",
        adding_headers={"X-Resource-Range": "0-10/10",},
    )

    results = list(manager.list())

    assert len(responses.calls) == 1

    assert len(results) == 10
    assert isinstance(results[0], FooModel)
