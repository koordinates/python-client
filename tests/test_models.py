import json
import unittest

import responses
from six.moves.urllib.parse import parse_qs, urlparse

from koordinates import base, Client
from koordinates.exceptions import ClientValidationError


class FooManager(base.Manager):
    TEST_LIST_URL = 'https://test.koordinates.com/services/v1/api/foo/'
    TEST_GET_URL = 'https://test.koordinates.com/services/v1/api/foo/%s'

    def list(self, *args, **kwargs):
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


class FooModel(base.Model):
    class Meta:
        manager = FooManager
        ordering_attributes = ['sortable']
        filter_attributes = ['filterable', 'thing', 'other', 'b1']


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(host='test.koordinates.com', token='test')
        self.mgr = FooManager(self.client)

    def test_manager_init(self):
        self.assert_(hasattr(FooModel, "_meta"))
        self.assert_(not hasattr(FooModel, "Meta"))
        self.assert_(FooModel._meta.manager is FooManager)
        self.assert_(FooManager.model is FooModel)

    def test_relations(self):
        m = FooModel()
        self.assert_(m._manager is None)
        self.assertRaises(ValueError, lambda: m._client)

    @responses.activate
    def test_manager_from_query(self):
        responses.add(responses.GET,
                      FooManager.TEST_GET_URL % 12345,
                      body='{"id": 12345}',
                      content_type='application/json')
        o = self.mgr.get(12345)
        self.assert_(isinstance(o, FooModel))
        self.assert_(o._manager is self.mgr)

    def test_deserialize(self):
        o = FooModel().deserialize({'id': '12345'}, self.mgr)
        self.assert_(isinstance(o, FooModel))
        self.assert_(o._manager is self.mgr)

        o = FooModel(id=1234, attr='test1')
        o2 = o.deserialize({'attr': 'test2', 'attr2': 'test3'}, self.mgr)
        self.assert_(o2 is o)
        self.assertEqual(o2.attr, 'test2')
        self.assertEqual(o2.id, 1234)
        self.assertEqual(o2.attr2, 'test3')

        mgr2 = FooManager(self.client)
        o = FooModel(id=1234)
        o._manager = self.mgr
        o2 = o.deserialize({}, mgr2)
        self.assert_(o2 is o)
        self.assertEqual(o2._manager, mgr2)

    def test_deserialize_list(self):
        o = FooModel().deserialize({
                'mylist': [1, 2],
                'created_at': ['2013-01-01', '2014-01-01'],
            }, self.mgr)
        self.assert_(isinstance(o.mylist, list))
        self.assertEqual(o.mylist, [1, 2])

    def test_serialize(self):
        o = FooModel(id=1234, attr='test')
        self.assertEqual(o.serialize(), {
            'attr': 'test',
            'id': 1234,
        })

    def test_init(self):
        o = FooModel()
        self.assert_(hasattr(o, 'id'))
        self.assertEqual(o.id, None)

        o = FooModel(id=123, bob='jim')
        self.assertEqual(o.id, 123)
        self.assertEqual(o.bob, 'jim')

    def test_str(self):
        m = FooModel(id=123)
        self.assertEqual(str(m), '123')

        # Incorporate title by default
        m.title = 'jim'
        self.assertEqual(str(m), '123 - jim')

        self.assertEqual(str(FooModel()), 'None')

    def test_repr(self):
        m = FooModel(id=123)
        self.assertEqual(repr(m), '<FooModel: 123>')

        # Incorporate title by default
        m.title = 'jim'
        self.assertEqual(repr(m), '<FooModel: 123 - jim>')

        self.assertEqual(repr(FooModel()), '<FooModel: None>')

    def test_bad_model_class(self):
        # Missing Meta
        try:
            class BadModel(base.Model):
                pass
        except AttributeError:
            pass
        else:
            assert False, "Should have received an AttributeError for not having a Meta: object"

        # Missing Meta.manager
        try:
            class BadModel2(base.Model):
                class Meta:
                    pass
        except AttributeError as e:
            pass
        else:
            assert False, "Should have received an AttributeError for not having Meta.manager set"


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(host='test.koordinates.com', token='test', activate_logging=True)
        self.foos = FooManager(self.client)

    def test_list(self):
        q = self.foos.list()
        self.assert_(isinstance(q, base.Query))
        self.assert_(q._manager is self.foos)
        self.assert_(q._target_url == FooManager.TEST_LIST_URL)

    def test_to_url(self):
        q = self.foos.list()
        self.assertEqual(q._to_url(), FooManager.TEST_LIST_URL)

    def test_order_by(self):
        base_q = self.foos.list()

        q = base_q.order_by('-sortable')
        self.assert_('sort=-sortable' in q._to_url())

        q = base_q.order_by('sortable')
        self.assert_('sort=sortable' in q._to_url())

        # should replace the previous sort
        q = base_q.order_by('-sortable')
        self.assert_('sort=-sortable' in q._to_url())
        self.assert_('sort=sortable' not in q._to_url())

    def test_order_by_invalud(self):
        base_q = self.foos.list()
        self.assertRaises(ClientValidationError, base_q.order_by, 'invalid')

    def test_clone(self):
        q0 = self.foos.list().filter(thing='bang')
        self.assertEqual(dict(q0._filters), {'thing': ['bang']})
        self.assertEqual(q0._order_by, None)

        q1 = q0.order_by('sortable')
        self.assertEqual(q1._order_by, 'sortable')
        self.assertEqual(q0._order_by, None)

        q1 = q0.filter(other='bob', thing='fred')
        self.assertEqual(dict(q0._filters), {'thing': ['bang']})
        self.assertEqual(dict(q1._filters), {'thing': ['bang', 'fred'], 'other': ['bob']})

    def test_filter(self):
        base_q = self.foos.list()

        q = base_q.filter(thing=1).filter(thing=2).filter(other='3', other__op=4).filter(b1='b2')

        self.assertEqual(dict(q._filters), {
            'thing': [1, 2],
            'other': ['3'],
            'other.op': [4],
            'b1': ['b2'],
        })

        # serialize:
        url = q._to_url()
        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual(params, {
            'thing': ['1', '2'],
            'other': ['3'],
            'other.op': ['4'],
            'b1': ['b2'],
        })

    def test_filter_invalid(self):
        base_q = self.foos.list()
        self.assertRaises(ClientValidationError, base_q.filter, invalid='test')

    def test_extra(self):
        base_q = self.foos.list().filter(thing='value')

        q = base_q.extra(some_key='some_value')
        self.assert_('some_key=some_value' in q._to_url())

        q = base_q.extra(thing='something_extra')
        url = q._to_url()
        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual(params, {
            'thing': ['value', 'something_extra'],
        })

    def test_expand(self):
        q0 = self.foos.list()
        self.assert_('Expand' not in q0._to_headers())

        q1 = self.foos.list().expand()
        self.assert_('Expand' in q1._to_headers())

    @responses.activate
    def test_count(self):
        responses.add(responses.GET,
                      FooManager.TEST_LIST_URL,
                      body="{}",
                      content_type='application/json',
                      adding_headers={'X-Resource-Range': '0-10/28'})

        q = self.foos.list()
        count = len(q)
        self.assertEqual(count, 28)

        # Second hit shouldn't do another request
        count = len(q)
        self.assertEqual(count, 28)

        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_pagination(self):
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL,
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(10)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '0-10/28',
                'Link': '<%s?page=2>; rel="page-next"' % FooManager.TEST_LIST_URL,
            },
        )
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL + '?page=2',
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(10, 20)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '10-20/28',
                'Link': '<%s?page=3>; rel="page-next"' % FooManager.TEST_LIST_URL,
            },
        )
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL + '?page=3',
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(20, 28)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '20-28/28',
            },
        )

        q = self.foos.list()
        for i, o in enumerate(q):
            continue

        self.assertEqual(i, 27)  # 0-index
        self.assertEqual(len(responses.calls), 3)

        # Second hit shouldn't do another request
        count = len(q)
        self.assertEqual(count, 28)
        self.assertEqual(len(responses.calls), 3)

    @responses.activate
    def test_slicing(self):
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL,
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(10)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '0-10/28',
                'Link': '<%s?page=2>; rel="page-next"' % FooManager.TEST_LIST_URL,
            },
        )
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL + '?page=2',
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(10, 20)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '10-20/28',
                'Link': '<%s?page=3>; rel="page-next"' % FooManager.TEST_LIST_URL,
            },
        )
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL + '?page=3',
            match_querystring=True,
            body=json.dumps([{'id': id} for id in range(20, 28)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '20-28/28',
            },
        )

        q = self.foos.list()
        for i, o in enumerate(q[:3]):
            self.assert_(isinstance(o, FooModel))

        self.assertEqual(i, 2)  # 0-index
        self.assertEqual(len(responses.calls), 1)

        # When the slice is bigger than the dataset
        for i, o in enumerate(q[:50]):
            continue

        self.assertEqual(i, 27)  # 0-index
        self.assertEqual(len(responses.calls), 4)

        # Bad slices, we only support query[:N] where N>0
        self.assertRaises(ValueError, lambda qq: qq[0], q)
        self.assertRaises(ValueError, lambda qq: qq[0:10], q)
        self.assertRaises(ValueError, lambda qq: qq[10:20], q)
        self.assertRaises(ValueError, lambda qq: qq[:10:3], q)
        self.assertRaises(ValueError, lambda qq: qq[:-5], q)
        self.assertRaises(ValueError, lambda qq: qq[:0], q)
        self.assertRaises(ValueError, lambda qq: qq[1:30:2], q)

    @responses.activate
    def test_list_cast(self):
        # Test that ``list(query)`` doesn't make an extra HEAD request
        responses.add(
            responses.HEAD,
            FooManager.TEST_LIST_URL,
            body="",
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '0-10/10',
            },
        )
        responses.add(
            responses.GET,
            FooManager.TEST_LIST_URL,
            body=json.dumps([{'id': id} for id in range(10)]),
            content_type='application/json',
            adding_headers={
                'X-Resource-Range': '0-10/10',
            },
        )

        results = list(self.foos.list())

        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(len(results), 10)
        self.assert_(isinstance(results[0], FooModel))
