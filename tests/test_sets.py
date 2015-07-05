import unittest

import responses

from koordinates import Set, Connection

from response_data.responses_3 import sets_single_good_simulated_response
from response_data.responses_4 import sets_multiple_good_simulated_response


class TestSets(unittest.TestCase):
    def setUp(self):
        self.conn = Connection('test')

    @responses.activate
    def test_get_set_by_id(self, id=1474):
        the_response = sets_single_good_simulated_response

        responses.add(responses.GET,
                      self.conn.get_url('SET', 'GET', 'single', {'id':1474}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.conn.sets.get(id)
        self.assert_(isinstance(obj, Set))

        self.assertEqual(obj.title,
                         "Ultra Fast Broadband Initiative Coverage")
        #FIXME: should be group.name as obj.group is a Group instance
        self.assertEqual(obj.group['name'],
                         "New Zealand Broadband Map")
        self.assertEqual(obj.url_html,
                         "https://koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/")

    @responses.activate
    def test_get_set_set_returns_all_rows(self):
        the_response = sets_multiple_good_simulated_response

        responses.add(responses.GET,
                      self.conn.get_url('SET', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_sets_returned = 0

        for layer in self.conn.sets.list():
            cnt_of_sets_returned += 1

        self.assertEqual(cnt_of_sets_returned, 2)
