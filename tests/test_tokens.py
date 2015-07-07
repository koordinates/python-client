from datetime import datetime
import json
import unittest

import responses

from koordinates import Token, Client

from response_data.tokens import (
    token_get_multiple_tokens_good_response,
    token_get_single_token_good_response,
    token_good_create,
)


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')

    @responses.activate
    def test_get_all_tokens_for_user(self):
        the_response = token_get_multiple_tokens_good_response

        responses.add(responses.GET,
                      self.client.get_url('TOKEN', 'GET', 'multi'),
                      body=the_response, status=200,
                      content_type='application/json')

        cnt_of_sets_returned = 0
        is_first = True

        for token in self.client.tokens.list():
            cnt_of_sets_returned += 1
            if is_first:
                is_first = False
                self.assertEqual(token.name, "")
                self.assertEqual(token.key_hint, "0fooxx...")
                self.assertEqual(token.url, "https://test.koordinates.com/services/api/v1/tokens/987654/")
                self.assert_(token._is_bound)
        self.assertEqual(cnt_of_sets_returned, 1)

    @responses.activate
    def test_get_individual_tokens_by_id(self):
        the_response = token_get_single_token_good_response

        responses.add(responses.GET,
                      self.client.get_url('TOKEN', 'GET', 'single', {'id':987654}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj_tok = self.client.tokens.get(987654)

        self.assert_(isinstance(obj_tok, Token))
        self.assert_(obj_tok._is_bound)

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
                      self.client.get_url('TOKEN', 'POST', 'create'),
                      body=the_response, status=200,
                      content_type='application/json')

        obj_tok = Token(name='Sample Token for Testing')
        obj_tok.scope = "query tiles catalog wxs:wfs wxs:wms wxs:wcs documents:read documents:write layers:read layers:write sets:read sets:write sources:read sources:write users:read users:write tokens:read tokens:write"
        obj_tok.expires_at = '2015-08-01T08:00:00Z'
        obj_tok_new = self.client.tokens.create(obj_tok, 'foo@example.com', 'foobar')

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
                      self.client.get_url('TOKEN', 'DELETE', 'single', {'id':987654}),
                      body=the_response, status=204,
                      content_type='application/json')

        self.client.tokens.delete(987654)

    @responses.activate
    def test_update_token(self):
        the_response = token_get_single_token_good_response

        responses.add(responses.GET,
                      self.client.get_url('TOKEN', 'GET', 'single', {'id':987654}),
                      body=the_response, status=200,
                      content_type='application/json')

        responses.add(responses.PUT,
                      self.client.get_url('TOKEN', 'PUT', 'update', {'id':987654}),
                      body=the_response, status=200,
                      content_type='application/json')

        obj_tok = self.client.tokens.get(987654)
        self.assert_(isinstance(obj_tok, Token))

        obj_tok.expires_at = datetime(2011, 1, 2, 3, 45)
        obj_tok.scopes = ['layers:read', 'layers:write']

        self.assertEqual(obj_tok.scope, 'layers:read layers:write')

        obj_tok.save()

        self.assertEqual(len(responses.calls), 2)

        req = json.loads(responses.calls[1].request.body)
        self.assertEqual(req['scope'], 'layers:read layers:write')
        self.assertEqual(req['expires_at'], '2011-01-02T03:45:00')

        # reset to server values
        self.assertEqual(len(obj_tok.scopes), 18)
