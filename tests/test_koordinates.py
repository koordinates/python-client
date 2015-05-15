#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_koordinates
----------------------------------

Tests for `koordinates` module.
"""
#from __future__ import unicode_literals
#from __future__ import absolute_import

import unittest
import responses
import requests

import sys
sys.path.append('/home/rshea/dev/koordinates-python-client/python-client')
import koordinates


class TestKoordinates(unittest.TestCase):

    def setUp(self):
        pass

    @responses.activate
    def test_use_of_responses(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                    body='{"error": "not found"}', status=404,
                    content_type='application/json')
 
        resp = requests.get('http://twitter.com/api/1/foobar')
 
        assert resp.json() == {"error": "not found"}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://twitter.com/api/1/foobar'
        assert responses.calls[0].response.text == '{"error": "not found"}'
 
    def test_sample(self):
        assert len("x") == 1 

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
