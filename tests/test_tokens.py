import unittest

import responses

from koordinates import Token, Connection

from response_data.responses_10 import token_get_multiple_tokens_good_response
from response_data.responses_10 import token_get_single_token_good_response
from response_data.responses_10 import token_good_create


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


    @responses.activate
    def test_create_token_good(self):
        the_response = token_good_create

        responses.add(responses.POST,
                      self.conn.get_url('TOKEN', 'POST', 'create'),
                      body=the_response, status=200,
                      content_type='application/json')

        obj_tok = Token(name='Sample Token for Testing')
        obj_tok.scope = "query tiles catalog wxs:wfs wxs:wms wxs:wcs documents:read documents:write layers:read layers:write sets:read sets:write sources:read sources:write users:read users:write tokens:read tokens:write"
        obj_tok.expires_at = '2015-08-01T08:00:00Z'
        obj_tok_new = self.conn.tokens.create(obj_tok, 'foo@example.com', 'foobar')

        self.assert_(isinstance(obj_tok_new, Token))

        self.assertEqual(obj_tok_new.name, "Sample Token for Testing")
        self.assertEqual(obj_tok_new.key_hint, "7fooxx...")
        self.assertEqual(obj_tok_new.url, "https://test.koordinates.com/services/api/v1/tokens/987659/")
        self.assertEqual(obj_tok_new.created_at.year, 2015)
        self.assertEqual(obj_tok_new.created_at.hour, 1)
        self.assertEqual(obj_tok_new.expires_at.year, 2015)
        self.assertEqual(obj_tok_new.expires_at.hour, 8)
        self.assertEqual(obj_tok_new.key, '77777777777777777777777777777777')

    @responses.activate
    def test_delete_token_good(self):

        the_response = ""

        responses.add(responses.DELETE, 
                      self.conn.get_url('TOKEN', 'DELETE', 'single', {'id':987654}),
                      body=the_response, status=204,
                      content_type='application/json')

        self.conn.tokens.delete(987654)

