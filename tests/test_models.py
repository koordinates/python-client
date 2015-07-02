import unittest

from six.moves.urllib.parse import parse_qs, urlparse

from koordinates import base, Connection
from koordinates.exceptions import NotAValidBasisForOrdering


class FooManager(base.Manager):
    TEST_LIST_URL = 'https://test.koordinates.com/services/v1/api/foo/'
    TEST_GET_URL = 'https://test.koordinates.com/services/v1/api/foo/%s'

    def get(self, foo_id):
        target_url = self.TEST_GET_URL % foo_id
        return super(FooManager, self).get(target_url, foo_id)

    def list(self):
        target_url = self.TEST_LIST_URL
        return super(FooManager, self).list(target_url)


class FooModel(base.Model):
    class Meta:
        manager = FooManager
        attribute_sort_candidates = ['sortable']


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.conn = Connection('test', 'test')
        FooModel._meta.manager.connection = self.conn

    def test_manager_init(self):
        self.assert_(hasattr(FooModel, "_meta"))
        self.assert_(not hasattr(FooModel, "Meta"))
        self.assert_(isinstance(FooModel._meta.manager, FooManager))

        mgr = FooModel._meta.manager
        self.assertEqual(mgr.model, FooModel)

    def test_relations(self):
        self.assert_(isinstance(FooModel._meta.manager, FooManager))


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.conn = Connection('test', 'test')
        self.foos = FooModel._meta.manager
        self.foos.connection = self.conn

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
        self.assertRaises(NotAValidBasisForOrdering, base_q.order_by, 'invalid')

        q = base_q.order_by('-sortable')
        self.assert_('sort=-sortable' in q._to_url())

        q = base_q.order_by('sortable')
        self.assert_('sort=sortable' in q._to_url())

        # should replace the previous sort
        q = base_q.order_by('-sortable')
        self.assert_('sort=-sortable' in q._to_url())
        self.assert_('sort=sortable' not in q._to_url())

    def test_clone(self):
        q0 = self.foos.list().filter(wiz='bang')
        self.assertEqual(dict(q0._filters), {'wiz': ['bang']})
        self.assertEqual(q0._order_by, None)

        q1 = q0.order_by('sortable')
        self.assertEqual(q1._order_by, 'sortable')
        self.assertEqual(q0._order_by, None)

        q1 = q0.filter(jim='bob', wiz='fred')
        self.assertEqual(dict(q0._filters), {'wiz': ['bang']})
        self.assertEqual(dict(q1._filters), {'wiz': ['bang', 'fred'], 'jim': ['bob']})

    def test_filters(self):
        base_q = self.foos.list()
        q = base_q.filter(thing=1).filter(thing=2).filter(other='3', other__op=4).filter(b1='b2')

        self.assertEqual(q._filters, {
            'thing': [1, 2],
            'other': ['3'],
            'other__op': [4],
            'b1': ['b2'],
        })

        # serialize:
        url = q._to_url()
        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual(params, {
            'thing': ['1', '2'],
            'other': ['3'],
            'other__op': ['4'],
            'b1': ['b2'],
        })

    def test_expand(self):
        q0 = self.foos.list()
        self.assert_('Expand' not in q0._to_headers())

        q1 = self.foos.list().expand()
        self.assert_('Expand' in q1._to_headers())
