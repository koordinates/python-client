import unittest

import responses

from koordinates import LayerPermission, Client, Group

from response_data.responses_10 import layer_list_permissions_good_simulated_response


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
