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
#import httpretty

import sys
sys.path.append('/home/rshea/dev/koordinates-python-client/python-client')
#from koordinates import koordinates
import koordinates


class TestKoordinates(unittest.TestCase):

    def setUp(self):
        pass

#   @httpretty.activate
#   def test_one(foo):
#       httpretty.enable()  # enable HTTPretty so that it will monkey patch the socket module
#       httpretty.register_uri(httpretty.GET, "http://yipit.com/",
#                              body="Find the best daily deals")

#       response = requests.get('http://yipit.com')

#       assert response.text == "Find the best daily deals"

#       httpretty.disable()  # disable afterwards, so that you will have no problems in code that uses that socket module
#       httpretty.reset()    # reset HTTPretty state (clean up registered urls and request history)

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
    #unittest.main(module="test_koordinates")
    unittest.main()
