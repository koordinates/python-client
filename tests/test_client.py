# -*- coding: utf-8 -*-

"""
Tests for the `koordinates.catalog` module.
"""
from __future__ import unicode_literals, absolute_import, print_function

import json
import re

import pytest
import responses
import six

from koordinates import Client, BadRequest

if six.PY2:
    from test.test_support import EnvironmentVarGuard
else:
    from test.support import EnvironmentVarGuard


@pytest.fixture
def client():
    return Client(host='test.koordinates.com', token='12345abcde')


def test_token_from_env():
    with EnvironmentVarGuard() as env:
        env.unset("KOORDINATES_TOKEN")
        with pytest.raises(KeyError):
            Client(host='test.koordinates.com')

        env.set("KOORDINATES_TOKEN", 'abcde12345')
        client = Client(host='test.koordinates.com')
        assert client.token == 'abcde12345'


def test_token_from_param():
    with EnvironmentVarGuard() as env:
        env.unset("KOORDINATES_TOKEN")
        client = Client(host='test.koordinates.com', token='12345abcde')
        assert client.token == '12345abcde'

        env.set("KOORDINATES_TOKEN", "don't use me")
        client = Client(host='test.koordinates.com', token='12345abcde')
        assert client.token == '12345abcde'


def test_get_url_path(client):
    assert '/layers/' == client.get_url_path('LAYER', 'GET', 'multi')
    assert '/publish/12345/' == client.get_url_path('PUBLISH', 'DELETE', 'single', {'id': 12345})


def test_get_url(client):
    url = client.get_url('LAYER', 'GET', 'multi')
    assert url == 'https://test.koordinates.com/services/api/v1/layers/'

    url = client.get_url('PUBLISH', 'DELETE', 'single', {'id': 12345})
    assert url == 'https://test.koordinates.com/services/api/v1/publish/12345/'


def test_reverse_url(client):
    params = client.reverse_url('LAYER', 'https://test.koordinates.com/services/api/v1/layers/12345/')
    assert params == {'id': '12345'}

    params = client.reverse_url('VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/')
    assert params == {'layer_id': '12345', 'version_id': '3456'}

    params = client.reverse_url('VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/versions/3456/publish/', verb='POST', urltype='publish')
    assert params == {'layer_id': '12345', 'version_id': '3456'}

    params = client.reverse_url('LICENSE', 'https://test.koordinates.com/services/api/v1/licenses/cc-by/nz/', verb='GET', urltype='cc')
    assert params == {'slug': 'cc-by', 'jurisdiction': 'nz'}

    with pytest.raises(KeyError):
        client.reverse_url('VERSION', '')
    with pytest.raises(KeyError):
        client.reverse_url('VERSION', 'https://test.koordinates.com/services/api/v1/layers/12345/')
    with pytest.raises(KeyError):
        client.reverse_url('VERSION', None)
    with pytest.raises(KeyError):
        client.reverse_url('VERSION', '/layers/12345/versions/3456/')


@responses.activate
def test_user_agent(client):
    responses.add(responses.GET,
                  'https://test.koordinates.com/api/v1/test/',
                  body='[]', status=200,
                  content_type='application/json')

    r = client.request('GET', 'https://test.koordinates.com/api/v1/test/')
    r.raise_for_status()

    req = responses.calls[0].request
    ua = req.headers.get('User-Agent')
    assert ua.startswith('KoordinatesPython/')


@responses.activate
def test_server_error(client):
    responses.add(responses.POST,
                  'https://test.koordinates.com/api/v1/layers/123/versions/',
                  body='{"autoupdate_schedule":["This field is required when autoupdate is on."]}',
                  status=400,
                  content_type='application/json')

    with pytest.raises(BadRequest) as cm:
        client.request('POST', 'https://test.koordinates.com/api/v1/layers/123/versions/', json={})

    e = cm.value
    assert str(e) == 'autoupdate_schedule: This field is required when autoupdate is on.'
    assert repr(e) == "BadRequest('autoupdate_schedule: This field is required when autoupdate is on.')"

    responses.add(responses.POST,
                  'https://test.koordinates.com/api/v1/layers/1234/versions/',
                  body='{"autoupdate_schedule":["This field is required when autoupdate is on."], "number":["Value must be >10", "Value must be <100"]}',
                  status=400,
                  content_type='application/json')

    with pytest.raises(BadRequest) as cm:
        client.request('POST', 'https://test.koordinates.com/api/v1/layers/1234/versions/', json={})

    e = cm.value
    estr = set(str(e).split('\n'))
    assert estr == {
        'number: Value must be >10; Value must be <100',
        'autoupdate_schedule: This field is required when autoupdate is on.',
    }
    assert repr(e) == "BadRequest('%s')" % str(e)


@responses.activate
def test_request_logging(client, caplog):
    responses.add(responses.GET,
                  'https://test.koordinates.com/api/v1/test/',
                  body='[]', status=200,
                  content_type='application/json')

    r = client.request('GET', 'https://test.koordinates.com/api/v1/test/', json={'some': ['data', 1]}, headers={"FooHeader": "Bar"})
    r.raise_for_status()


    lreq = caplog.records[0]
    lmsg = lreq.getMessage()
    assert lmsg.startswith('Request: ')

    lf = re.match('^Request: GET https://test.koordinates.com/api/v1/test/ headers=(?P<headers>.*) body=(?P<body>.*)$', lmsg)
    print(lf.group('headers'), lf.group('body'))

    lbody = json.loads(lf.group('body'))
    assert lbody == {'some': ['data', 1]}

    lheaders = json.loads(lf.group('headers'))
    assert 'FooHeader' in lheaders
    assert 'Authorization' not in lheaders
