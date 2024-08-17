import json

import pytest
import responses

from koordinates import base, Client
from koordinates.utils import is_bound


class FooManager(base.Manager):
    TEST_LIST_URL = "https://test.koordinates.com/services/v1/api/foo/"
    TEST_GET_URL = "https://test.koordinates.com/services/v1/api/foo/%s/"
    _URL_KEY = "TEST_FOO"

    def __init__(self, client, *args, **kwargs):
        super(FooManager, self).__init__(client, *args, **kwargs)
        self.pops = PopManager(client, self)

    def list(self):
        """
        Fetches a set of Tokens
        """
        return base.Query(self, self.TEST_LIST_URL)

    def get(self, id, expand=[]):
        """Fetches a Token determined by the value of `id`.

        :param id: ID for the new :class:`Token`  object.
        """
        target_url = self.TEST_GET_URL % id
        return self._get(target_url, expand=expand)

    def list_custom_attrs(self):
        return base.Query(
            self,
            self.TEST_LIST_URL,
            valid_filter_attributes=("custom",),
            valid_sort_attributes=("custom",),
        )


class FooModel(base.Model):
    class Meta:
        manager = FooManager
        ordering_attributes = ["sortable"]
        filter_attributes = ["filterable", "thing", "other", "b1"]
        serialize_skip = ["noserialize"]
        relations = {
            "bars": ["BarModel"],
        }

    def _deserialize(self, data, manager):
        super(FooModel, self)._deserialize(data, manager)
        self.pop = (
            PopModel()._deserialize(data["pop"], manager.pops, self)
            if data.get("pop")
            else None
        )
        return self

    @is_bound
    def test_is_bound(self):
        pass


class Foo2Model(FooModel):
    # child model
    class Meta:
        manager = FooManager


# Bar is a related model of foo (ala /foo/123/bar/456)
class BarManager(base.Manager):
    _URL_KEY = "TEST_BAR"


class BarModel(base.Model):
    class Meta:
        manager = BarManager
        relations = {
            "foo": FooModel,
        }


# Pop is an inner model, that lives as Foo.pop at /foo/123/
class PopManager(base.InnerManager):
    pass


class PopModel(base.InnerModel):
    class Meta:
        manager = PopManager


@pytest.fixture
def client():
    client = Client(host="test.koordinates.com", token="test")
    client.mgr = FooManager(client)

    client._register_manager(FooModel, client.mgr)
    client._register_manager(BarModel, BarManager(client))

    client._URL_TEMPLATES["v1"].update(
        {
            "TEST_FOO": {
                "GET": {
                    "multi": "foo/",
                    "single": "foo/{id}/",
                }
            },
            "TEST_BAR": {
                "GET": {
                    "multi": "foo/{foo_id}/bar/",
                    "single": "foo/{foo_id}/bar/{id}/",
                }
            },
        }
    )
    return client


class TestModels(object):
    def test_manager_init(self):
        assert hasattr(FooModel, "_meta")
        assert not hasattr(FooModel, "Meta")
        assert FooModel._meta.manager is FooManager
        assert FooManager.model is FooModel

    def test_relations(self):
        m = FooModel()
        assert m._manager is None
        with pytest.raises(ValueError):
            m._client

    @responses.activate
    def test_manager_from_query(self, client):
        responses.add(
            responses.GET,
            FooManager.TEST_GET_URL % 12345,
            body='{"id": 12345}',
            content_type="application/json",
        )
        o = client.mgr.get(12345)
        assert isinstance(o, FooModel)
        assert o._manager is client.mgr

    def test_deserialize(self, client):
        o = FooModel()._deserialize({"id": "12345"}, client.mgr)
        assert isinstance(o, FooModel)
        assert o._manager is client.mgr

        o = FooModel(id=1234, attr="test1")
        o2 = o._deserialize({"attr": "test2", "attr2": "test3"}, client.mgr)
        assert o2 is o
        assert o2.attr == "test2"
        assert o2.id == 1234
        assert o2.attr2 == "test3"

        mgr2 = FooManager(client)
        o = FooModel(id=1234)
        o._manager = client.mgr
        o2 = o._deserialize({}, mgr2)
        assert o2 is o
        assert o2._manager == mgr2

    def test_deserialize_list(self, client):
        o = FooModel()._deserialize(
            {
                "mylist": [1, 2],
                "created_at": ["2013-01-01", "2014-01-01"],
            },
            client.mgr,
        )
        assert isinstance(o.mylist, list)
        assert o.mylist == [1, 2]

    def test_serialize(self):
        o = FooModel(id=1234, attr="test", noserialize=1)
        assert o._serialize() == {
            "attr": "test",
            "id": 1234,
        }

    def test_equality(self, client):
        o1 = FooModel()._deserialize({"id": "12345"}, client.mgr)
        o2 = FooModel()._deserialize({"id": "12345"}, client.mgr)
        o3 = FooModel()._deserialize({"id": "23456"}, client.mgr)

        assert o1 == o2
        assert not o1 != o2
        assert o1 != o3
        assert not o1 == o3

        o4 = Foo2Model()._deserialize({"id": "12345"}, client.mgr)
        assert o1 == o4

        o5 = BarModel()._deserialize({"id": "12345"}, BarManager(client))
        assert o1 != o5

    @responses.activate
    def test_serialize2(self, client):
        FOO_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "foo",
            "bars": FooManager.TEST_GET_URL % "12345/bars",
        }
        BAR_INNER_DATA = {
            "id": 23456,
            "url": FooManager.TEST_GET_URL % "12345/bar/23456",
            "name": "bar",
            "foo": FooManager.TEST_GET_URL % 12345,
        }
        bar_mgr = BarManager(client)

        o_foo = FooModel()._deserialize(FOO_DATA, client.mgr)
        o_bar = BarModel()._deserialize(BAR_INNER_DATA, bar_mgr)

        responses.add(
            responses.GET,
            FooManager.TEST_GET_URL % 12345,
            body='{"id": 12345}',
            content_type="application/json",
        )
        foo2 = o_bar.get_foo()
        assert isinstance(foo2, FooModel)
        assert foo2.id == 12345

        responses.add(
            responses.GET,
            FooManager.TEST_GET_URL % "12345/bars",
            body="[]",
            content_type="application/json",
        )
        assert isinstance(o_foo.list_bars(), base.Query)
        assert list(o_foo.list_bars()) == []

    def test_inner_load(self, client):
        FOO_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "foo",
            "pop": {
                "id": 3456,
                "type": "double-happy",
            },
        }
        o_foo = FooModel()._deserialize(FOO_DATA, client.mgr)

        assert isinstance(o_foo.pop, PopModel)
        assert o_foo.pop.type == "double-happy"
        o_foo.pop.type = "roman-candle"

        z = o_foo._serialize()
        assert z["pop"]["type"] == "roman-candle"

    def test_inner_set(self, client):
        FOO_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "foo",
            "pop": None,
        }
        o_foo = FooModel()._deserialize(FOO_DATA, client.mgr)

        p = PopModel(id=23456, type="double-happy")
        o_foo.pop = p

        assert hasattr(p, "_parent")
        assert p._parent is o_foo

        z = o_foo._serialize()
        assert z["pop"]["type"] == "double-happy"

    def test_inner_rel(self, client):
        FOO_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "foo",
            "pop": {
                "id": 3456,
                "type": "double-happy",
            },
        }
        o_foo = FooModel()._deserialize(FOO_DATA, client.mgr)
        o_pop = o_foo.pop
        assert isinstance(o_pop, PopModel)
        assert o_pop._parent is o_foo
        assert isinstance(o_pop._manager, PopManager)

    def test_init(self):
        o = FooModel()
        assert hasattr(o, "id")
        assert o.id == None

        o = FooModel(id=123, bob="jim")
        assert o.id == 123
        assert o.bob == "jim"

    def test_str(self):
        m = FooModel(id=123)
        assert str(m) == "123"

        # Incorporate title by default
        m.title = "jim"
        assert str(m) == "123 - jim"

        assert str(FooModel()) == "None"

    def test_repr(self):
        m = FooModel(id=123)
        assert repr(m) == "<FooModel: 123>"

        # Incorporate title by default
        m.title = "jim"
        assert repr(m) == "<FooModel: 123 - jim>"

        assert repr(FooModel()) == "<FooModel: None>"

    def test_bad_model_class(self):
        # Missing Meta
        try:

            class BadModel(base.Model):
                pass

        except AttributeError:
            pass
        else:
            assert (
                False
            ), "Should have received an AttributeError for not having a Meta: object"

        # Missing Meta.manager
        try:

            class BadModel2(base.Model):
                class Meta:
                    pass

        except AttributeError:
            pass
        else:
            assert (
                False
            ), "Should have received an AttributeError for not having Meta.manager set"

    def test_is_bound(self, client):
        url = FooManager.TEST_GET_URL % 123

        with pytest.raises(ValueError):
            # needs an id set
            FooModel().test_is_bound()

        with pytest.raises(ValueError):
            # needs a url set
            FooModel(id=123).test_is_bound()

        with pytest.raises(ValueError):
            # needs a manager set
            FooModel(id=123, url=url).test_is_bound()

        with pytest.raises(ValueError):
            # needs 'id' set
            f = client.mgr.create_from_result({})
            f.test_is_bound()

        # bound
        f = client.mgr.create_from_result({"id": 123, "url": url})
        f.test_is_bound()

    def test_inner_is_bound(self, client):
        FOO_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "foo",
            "pop": {
                "id": 3456,
                "type": "double-happy",
            },
        }
        o_foo = FooModel()._deserialize(FOO_DATA, client.mgr)
        o_pop = o_foo.pop
        assert o_foo._is_bound
        assert o_pop._is_bound
        o_foo.id = None
        assert not o_pop._is_bound

    @responses.activate
    def test_refresh(self, client):
        FOO_LIST_DATA = [
            {
                "id": 12345,
                "url": FooManager.TEST_GET_URL % 12345,
                "name": "Alpaca",
                "age": 1,
            }
        ]
        FOO_GET_DATA = {
            "id": 12345,
            "url": FooManager.TEST_GET_URL % 12345,
            "name": "Alpaca",
            "age": 1,
            "species": "Vicugna pacos",
        }
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL,
            body=json.dumps(FOO_LIST_DATA),
            content_type="application/json",
        )

        responses.add(
            responses.GET,
            FooManager.TEST_GET_URL % 12345,
            body=json.dumps(FOO_GET_DATA),
            content_type="application/json",
        )

        foo = client.mgr.list()[:1][0]
        assert isinstance(foo, FooModel)

        pytest.raises(AttributeError, getattr, foo, "species")
        foo.age = 3

        f = foo.refresh()
        assert f is foo
        assert foo.species == "Vicugna pacos"
        assert foo.age == 1
