import json
import unittest

import responses

from koordinates import Set, Client, Group

from response_data.responses_3 import sets_single_good_simulated_response
from response_data.responses_4 import sets_multiple_good_simulated_response


class TestSets(unittest.TestCase):
    def setUp(self):
        self.client = Client('koordinates.com', token='test')

    @responses.activate
    def test_get_set_by_id(self, id=1474):
        the_response = sets_single_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('SET', 'GET', 'single', {'id':1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.client.sets.get(id)
        self.assert_(isinstance(obj, Set))

        self.assertEqual(obj.title,
                         "Ultra Fast Broadband Initiative Coverage")
        self.assertEqual(obj.group.name,
                         "New Zealand Broadband Map")
        self.assertEqual(obj.url_html,
                         "https://koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/")

    @responses.activate
    def test_get_set_set_returns_all_rows(self):
        the_response = sets_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.client.get_url('SET', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_sets_returned = 0

        for layer in self.client.sets.list():
            cnt_of_sets_returned += 1

        self.assertEqual(cnt_of_sets_returned, 2)

    @responses.activate
    def test_set_create(self):
        responses.add(responses.POST,
                      self.client.get_url('SET', 'POST', 'create'),
                      body=sets_single_good_simulated_response, status=201,
                      adding_headers={"Location": "https://koordinates.com/services/api/v1/sets/933/"})

        responses.add(responses.GET,
                      self.client.get_url('SET', 'GET', 'single', {'id': 933}),
                      body=sets_single_good_simulated_response, status=200)

        s = Set()
        s.title = 'test title'
        s.description = 'description'
        s.group = 141
        s.items = [
            "https://koordinates.com/services/api/v1/layers/4226/",
            "https://koordinates.com/services/api/v1/layers/4228/",
            "https://koordinates.com/services/api/v1/layers/4227/",
            "https://koordinates.com/services/api/v1/layers/4061/",
            "https://koordinates.com/services/api/v1/layers/4147/",
            "https://koordinates.com/services/api/v1/layers/4148/",
        ]

        rs = self.client.sets.create(s)
        self.assert_(rs is s)
        self.assert_(isinstance(s.group, Group))
        self.assertEqual(s.group.id, 141)

        self.assertEqual(len(responses.calls), 2)

        req = json.loads(responses.calls[0].request.body)
        self.assertEqual(len(req['items']), 6)
        self.assertEqual(req['group'], 141)


    @responses.activate
    def test_set_update(self):
        responses.add(responses.GET,
                      self.client.get_url('SET', 'GET', 'single', {'id': 933}),
                      body=sets_single_good_simulated_response, status=200)

        responses.add(responses.PUT,
                      self.client.get_url('SET', 'PUT', 'update', {'id': 933}),
                      body=sets_single_good_simulated_response, status=200)

        s = self.client.sets.get(933)
        self.assertEqual(s.id, 933)

        s.items = [
            "https://koordinates.com/services/api/v1/layers/4226/",
        ]
        s.save()
        self.assertEqual(len(responses.calls), 2)

        req = json.loads(responses.calls[1].request.body)
        self.assertEqual(len(req['items']), 1)

        # reset to the server-provided values
        self.assertEqual(len(s.items), 6)
