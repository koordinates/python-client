import unittest

import responses

from koordinates import Token, Connection

from response_data.responses_10 import token_get_multiple_tokens_good_response
from response_data.responses_10 import token_get_single_token_good_response


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.conn = Connection('test')

    @responses.activate
    def test_get_all_tokens_for_user(self):
        the_response = token_get_multiple_tokens_good_response

        responses.add(responses.GET,
                      self.conn.get_url('TOKEN', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        obj = self.conn.tokens.list()

        cnt_of_sets_returned = 0
        is_first = True

        for token in self.conn.tokens.list():
            cnt_of_sets_returned += 1
            if is_first:
                is_first = False
                self.assertEqual(token.name, "")
                self.assertEqual(token.key_hint, "0fooxx...")
                self.assertEqual(token.url, "https://test.koordinates.com/services/api/v1/tokens/987654/")
        self.assertEqual(cnt_of_sets_returned, 1)

    @responses.activate
    def test_get_individual_tokens_by_id(self):
        the_response = token_get_single_token_good_response

        responses.add(responses.GET,
                      self.conn.get_url('TOKEN', 'GET', 'single', {'id':987654}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj_tok = self.conn.tokens.get(987654)

        self.assert_(isinstance(obj_tok, Token))

        self.assertEqual(obj_tok.name, "")
        self.assertEqual(obj_tok.key_hint, "0fooxx...")
        self.assertEqual(obj_tok.url, "https://test.koordinates.com/services/api/v1/tokens/987654/")
        self.assertEqual(obj_tok.created_at.year, 2015)
        self.assertEqual(obj_tok.created_at.hour, 5)
        self.assertEqual(obj_tok.expires_at, None)
