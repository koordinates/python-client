import unittest

import responses

from koordinates import SourcePermission, DocumentPermission, TablePermission, SetPermission, LayerPermission
from koordinates import Client, Group, User

from response_data.responses_10 import *


class TestSets(unittest.TestCase):
    def setUp(self):
        self.client = Client('koordinates.com', token='test')

    @responses.activate
    def test_get_layer_permissions_by_id(self, id=4):
        the_response = layer_list_permissions_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'layer', {'layer_id': id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.client.layer_permissions.list(id):
            self.assert_(isinstance(obj, LayerPermission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "download")
            self.assertEqual(obj.id, "group.everyone")
            self.assertEqual(obj.group.id, 4)
            self.assertEqual(obj.group.name, "Everyone")
            self.assertEqual(obj.group.url, "https://koordinates.com/services/api/v1/groups/1/")
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 1)

    @responses.activate
    def test_get_set_permissions_by_id(self, id=1):
        the_response = set_list_permissions_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'set', {'set_id': id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.client.set_permissions.list(id):
            self.assert_(isinstance(obj, SetPermission))
            self.assertIn(obj.permission, ["admin", "view"])
            if obj.group:
                self.assert_(isinstance(obj.group, Group))
                self.assertEqual(obj.group.url, "https://koordinates.com/services/api/v1/groups/%s/" % obj.group.id)
            elif obj.user:
                self.assert_(isinstance(obj.user, User))
                self.assertEqual(obj.user.url, "https://koordinates.com/services/api/v1/users/%s/" % obj.user.id)
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 3)

    @responses.activate
    def test_get_table_permissions_by_id(self, id=1):
        the_response = table_list_permissions_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'table', {'table_id': id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.client.table_permissions.list(id):
            self.assert_(isinstance(obj, TablePermission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "download")
            self.assertEqual(obj.id, "group.everyone")
            self.assertEqual(obj.group.id, 1)
            self.assertEqual(obj.group.name, "Everyone")
            self.assertEqual(obj.group.url, "https://koordinates.com/services/api/v1/groups/1/")
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 1)

    @responses.activate
    def test_get_document_permissions_by_id(self, id=1):
        the_response = document_list_permissions_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'document', {'document_id': id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.client.document_permissions.list(id):
            self.assert_(isinstance(obj, DocumentPermission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "view")
            self.assertEqual(obj.id, "group.everyone")
            self.assertEqual(obj.group.id, 1)
            self.assertEqual(obj.group.name, "Everyone")
            self.assertEqual(obj.group.url, "https://koordinates.com/services/api/v1/groups/1/")
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 1)

    @responses.activate
    def test_get_source_permissions_by_id(self, id=1):
        the_response = source_list_permissions_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'source', {'source_id': id}),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.client.source_permissions.list(id):
            self.assert_(isinstance(obj, SourcePermission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "admin")
            self.assertEqual(obj.id, "group.administrators")
            self.assertEqual(obj.group.id, 3)
            self.assertEqual(obj.group.name, "Site Administrators")
            self.assertEqual(obj.group.url, "https://koordinates.com/services/api/v1/groups/3/")
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 1)
