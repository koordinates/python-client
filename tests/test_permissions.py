import responses
import unittest

from koordinates import Permission
from koordinates import Client, Group, User

from response_data.responses_10 import layer_list_permissions_good_simulated_response, layer_permission_simulated_response
from response_data.responses_10 import set_permission_simulated_response, set_list_permissions_good_simulated_response
from response_data.responses_5 import layers_version_single_good_simulated_response
from response_data.responses_3 import sets_single_good_simulated_response


class TestLayerPermissions(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')
        self.layer = self.client.layers.get(1474)

    @responses.activate
    def test_list_layer_permissions(self):
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'multi')
        responses.add(responses.GET,
                      target_url,
                      body=layer_list_permissions_good_simulated_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.layer._permissions.list():
            self.assert_(isinstance(obj, Permission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "download")
            self.assertEqual(obj.id, "group.everyone")
            self.assertEqual(obj.group.id, 4)
            self.assertEqual(obj.group.name, "Everyone")
            self.assertEqual(obj.group.url, "https://test.koordinates.com/services/api/v1/groups/4/")
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 1)

    @responses.activate
    def test_create_layer_permission(self):
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'POST', 'single')
        responses.add(responses.POST,
                      target_url,
                      body=layer_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://test.koordinates.com/services/api/v1/layers/%s/permissions/%s/" % (self.layer.id, "108")})
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'single', {'permission_id': 108})
        responses.add(responses.GET,
                      target_url,
                      body=layer_permission_simulated_response, status=200)
        permission = Permission()
        permission.group = "108"
        permission.permission = "download"
        response = self.layer._permissions.create(permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, Permission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(108, permission.group.id)

    @responses.activate
    def test_set_layer_permissions(self):
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'PUT', 'multi')
        responses.add(responses.PUT,
                      target_url,
                      body=layer_list_permissions_good_simulated_response, status=201)
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'multi')
        responses.add(responses.GET,
                      target_url,
                      body=layer_list_permissions_good_simulated_response, status=200,
                      content_type='application/json')

        data = {
            "permission": "download",
            "group": "everyone"
        }

        for obj in self.layer._permissions.set(data):
            self.assert_(isinstance(obj, Permission))
            self.assert_(isinstance(obj.group, Group))
            self.assertEqual(obj.permission, "download")
            self.assertEqual(obj.id, "group.everyone")

    @responses.activate
    def test_get_layer_permission(self):
        base_url = self.client.get_url('LAYER', 'GET', 'single', {'id': self.layer.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'single', {'permission_id': 108})
        responses.add(responses.GET,
                      target_url,
                      body=layer_permission_simulated_response, status=200)

        response = self.layer._permissions.get(108)

        self.assertEqual(response.id, "group.108")
        self.assert_(isinstance(response, Permission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(108, response.group.id)


class TestSetPermissions(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')
        responses.add(responses.GET,
                      self.client.get_url('SET', 'GET', 'single', {'id': 933}),
                      body=sets_single_good_simulated_response, status=200,
                      content_type='application/json')
        self.set = self.client.sets.get(933)

    @responses.activate
    def test_list_set_permissions(self):

        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'multi')

        responses.add(responses.GET,
                      target_url,
                      body=set_list_permissions_good_simulated_response, status=200,
                      content_type='application/json')

        cnt_permissions_returned = 0
        for obj in self.set._permissions.list():
            self.assert_(isinstance(obj, Permission))
            self.assertIn(obj.permission, ["admin", "view"])
            if obj.group:
                self.assert_(isinstance(obj.group, Group))
                self.assertEqual(obj.group.url, "https://test.koordinates.com/services/api/v1/groups/%s/" % obj.group.id)
            elif obj.user:
                self.assert_(isinstance(obj.user, User))
                self.assertEqual(obj.user.url, "https://test.koordinates.com/services/api/v1/users/%s/" % obj.user.id)
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 3)

    @responses.activate
    def test_create_set_permission(self):
        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'POST', 'single')
        responses.add(responses.POST,
                      target_url,
                      body=set_permission_simulated_response, status=201,
                      adding_headers={"Location": "https://test.koordinates.com/services/api/v1/sets/%s/permissions/%s/" % (self.set.id, "34")})

        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'single', {'permission_id': 34})
        responses.add(responses.GET,
                      target_url,
                      body=set_permission_simulated_response, status=200)

        permission = Permission()
        permission.group = "34"
        permission.permission = "edit"
        response = self.set._permissions.create(permission)

        self.assertEqual(response.id, permission.id)
        self.assertEqual(response.permission, permission.permission)
        self.assert_(isinstance(response, Permission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(34, permission.group.id)

    @responses.activate
    def test_set_set_permissions(self):
        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'PUT', 'multi')
        responses.add(responses.PUT,
                      target_url,
                      body=set_list_permissions_good_simulated_response, status=201)
        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'multi')
        responses.add(responses.GET,
                      target_url,
                      body=set_list_permissions_good_simulated_response, status=200,
                      content_type='application/json')

        data = [
            {
                "permission": "admin",
                "user": "4"
            },
            {
                "permission": "admin",
                "group": "administrators"
            },
            {
                "permission": "view",
                "group": "everyone"
            },
        ]

        cnt_permissions_returned = 0
        for obj in self.set._permissions.set(data):
            self.assert_(isinstance(obj, Permission))
            self.assertIn(obj.permission, ["admin", "view"])
            if obj.group:
                self.assert_(isinstance(obj.group, Group))
                self.assertEqual(obj.group.url, "https://test.koordinates.com/services/api/v1/groups/%s/" % obj.group.id)
            elif obj.user:
                self.assert_(isinstance(obj.user, User))
                self.assertEqual(obj.user.url, "https://test.koordinates.com/services/api/v1/users/%s/" % obj.user.id)
            cnt_permissions_returned += 1

        self.assertEqual(cnt_permissions_returned, 3)

    @responses.activate
    def test_set_layer_permission(self):
        base_url = self.client.get_url('SET', 'GET', 'single', {'id': self.set.id})
        target_url = base_url + self.client.get_url_path('PERMISSION', 'GET', 'single', {'permission_id': 34})
        responses.add(responses.GET,
                      target_url,
                      body=set_permission_simulated_response, status=200)

        response = self.set._permissions.get(34)

        self.assertEqual(response.id, "group.34")
        self.assert_(isinstance(response, Permission))
        self.assert_(isinstance(response.group, Group))
        self.assertEqual(34, response.group.id)
