# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.catalog` module.
"""
from __future__ import unicode_literals, absolute_import

import unittest

import responses
import six

from koordinates import Client, BadRequest

if six.PY2:
    from test.test_support import EnvironmentVarGuard
else:
    from test.support import EnvironmentVarGuard


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(host='test.koordinates.com', token='12345abcde')

    def test_token_from_env(self):
        with EnvironmentVarGuard() as env:
            env.unset("KOORDINATES_TOKEN")
            self.assertRaises(KeyError, Client, host='test.koordinates.com')

            env.set("KOORDINATES_TOKEN", 'abcde12345')
            client = Client(host='test.koordinates.com')
            self.assertEqual(client.token, 'abcde12345')

    def test_token_from_param(self):
        with EnvironmentVarGuard() as env:
            env.unset("KOORDINATES_TOKEN")
            client = Client(host='test.koordinates.com', token='12345abcde')
            self.assertEqual(client.token, '12345abcde')

            env.set("KOORDINATES_TOKEN", "don't use me")
            client = Client(host='test.koordinates.com', token='12345abcde')
            self.assertEqual(client.token, '12345abcde')

    def test_get_url_path(self):
        self.assertEqual('/layers/', self.client.get_url_path('LAYER', 'GET', 'multi'))
        self.assertEqual('/publish/12345/', self.client.get_url_path('PUBLISH', 'DELETE', 'single', {'id': 12345}))

    def test_get_url(self):
        url = self.client.get_url('LAYER', 'GET', 'multi')
        self.assertEqual(url, 'https://test.koordinates.com/services/api/v1/layers/')

        url = self.client.get_url('PUBLISH', 'DELETE', 'single', {'id': 12345})
        self.assertEqual(url, 'https://test.koordinates.com/services/api/v1/publish/12345/')

    def test_reverse_url(self):
        params = self.client.reverse_url('LAYER', 'https://test.koordinates.com/services/api/v1/layers/12345/')
        self.assertEqual(params, {'id': '12345'})

        params = self.client.reverse_url('VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/')
        self.assertEqual(params, {'layer_id': '12345', 'version_id': '3456'})

        params = self.client.reverse_url('VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/publish/', verb='POST', urltype='publish')
        self.assertEqual(params, {'layer_id': '12345', 'version_id': '3456'})

        params = self.client.reverse_url('LICENSE', 'https://test.koordinates.com/services/api/v1/licenses/cc-by/nz/', verb='GET', urltype='cc')
        self.assertEqual(params, {'slug': 'cc-by', 'jurisdiction': 'nz'})

        self.assertRaises(KeyError, self.client.reverse_url, 'VERSION', '')
        self.assertRaises(KeyError, self.client.reverse_url, 'VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/')
        self.assertRaises(KeyError, self.client.reverse_url, 'VERSION', None)
        self.assertRaises(KeyError, self.client.reverse_url, 'VERSION', '/layers/12345/versions/3456/')

    @responses.activate
    def test_user_agent(self):
        responses.add(responses.GET,
                      'https://test.koordinates.com/api/v1/test/',
                      body='[]', status=200,
                      content_type='application/json')

        r = self.client.request('GET', 'https://test.koordinates.com/api/v1/test/')
        r.raise_for_status()

        req = responses.calls[0].request
        ua = req.headers.get('User-Agent')
        self.assert_(ua.startswith('KoordinatesPython/'))

    @responses.activate
    def test_server_error(self):
        responses.add(responses.POST,
                      'https://test.koordinates.com/api/v1/layers/123/versions/',
                      body='{"autoupdate_schedule":["This field is required when autoupdate is on."]}',
                      status=400,
                      content_type='application/json')

        with self.assertRaises(BadRequest) as cm:
            self.client.request('POST', 'https://test.koordinates.com/api/v1/layers/123/versions/', json={})

        e = cm.exception
        self.assertEqual(str(e), 'autoupdate_schedule: This field is required when autoupdate is on.')
        self.assertEqual(repr(e), "BadRequest('autoupdate_schedule: This field is required when autoupdate is on.')")

        responses.add(responses.POST,
                      'https://test.koordinates.com/api/v1/layers/1234/versions/',
                      body='{"autoupdate_schedule":["This field is required when autoupdate is on."], "number":["Value must be >10", "Value must be <100"]}',
                      status=400,
                      content_type='application/json')

        with self.assertRaises(BadRequest) as cm:
            self.client.request('POST', 'https://test.koordinates.com/api/v1/layers/1234/versions/', json={})

        e = cm.exception
        self.assertEqual(str(e), 'number: Value must be >10; Value must be <100\nautoupdate_schedule: This field is required when autoupdate is on.')
        self.assertEqual(repr(e), "BadRequest('number: Value must be >10; Value must be <100\nautoupdate_schedule: This field is required when autoupdate is on.')")
