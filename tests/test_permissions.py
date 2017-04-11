import unittest

import responses

from koordinates import SourcePermission, DocumentPermission, TablePermission, SetPermission, LayerPermission
from koordinates import Client, Group, User

from response_data.responses_10 import *


class TestPermissions(unittest.TestCase):
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

    @responses.activate
    def test_layer_permissions_create(self, id=4):
        responses.add(responses.POST,
                      self.client.get_url('PERMISSION', 'POST', 'layer', {'layer_id': id}),
                      body=layer_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/layers/%s/permissions/%s/" % (id, "108")})
        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'layer_single', {'layer_id': id, 'id': 108}),
                      body=layer_permission_simulated_response, status=200)
        permission = LayerPermission()
        permission.group = "group.108"
        permission.permission = "download"
        response = self.client.layer_permissions.create(id, permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, LayerPermission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(108, permission.group.id)

    @responses.activate
    def test_table_permissions_create(self, id=6):
        responses.add(responses.POST,
                      self.client.get_url('PERMISSION', 'POST', 'table', {'table_id': id}),
                      body=table_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/tables/%s/permissions/%s/" % (id, "123")})
        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'table_single', {'table_id': id, 'id': 123}),
                      body=table_permission_simulated_response, status=200)
        permission = TablePermission()
        permission.group = "group.123"
        permission.permission = "edit"
        response = self.client.table_permissions.create(id, permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, TablePermission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(123, permission.group.id)

    @responses.activate
    def test_set_permissions_create(self, id=9):
        responses.add(responses.POST,
                      self.client.get_url('PERMISSION', 'POST', 'set', {'set_id': id}),
                      body=set_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/sets/%s/permissions/%s/" % (id, "34")})
        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'set_single', {'set_id': id, 'id': 34}),
                      body=set_permission_simulated_response, status=200)
        permission = SetPermission()
        permission.group = "group.34"
        permission.permission = "edit"
        response = self.client.set_permissions.create(id, permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, SetPermission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(34, permission.group.id)

    @responses.activate
    def test_source_permissions_create(self, id=89):
        responses.add(responses.POST,
                      self.client.get_url('PERMISSION', 'POST', 'source', {'source_id': id}),
                      body=source_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/sources/%s/permissions/%s/" % (id, "67")})
        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'source_single', {'source_id': id, 'id': 67}),
                      body=source_permission_simulated_response, status=200)
        permission = SourcePermission()
        permission.group = "group.67"
        permission.permission = "edit"
        response = self.client.source_permissions.create(id, permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, SourcePermission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(67, permission.group.id)

    @responses.activate
    def test_document_permissions_create(self, id=99):
        responses.add(responses.POST,
                      self.client.get_url('PERMISSION', 'POST', 'document', {'document_id': id}),
                      body=document_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/documents/%s/permissions/%s/" % (id, "22")})
        responses.add(responses.GET,
                      self.client.get_url('PERMISSION', 'GET', 'document_single', {'document_id': id, 'id': 22}),
                      body=document_permission_simulated_response, status=200)
        permission = DocumentPermission()
        permission.group = "group.22"
        permission.permission = "edit"
        response = self.client.document_permissions.create(id, permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, DocumentPermission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(22, permission.group.id)
