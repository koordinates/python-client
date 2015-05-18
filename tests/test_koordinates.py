#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_koordinates
----------------------------------

Tests for `koordinates` module.
"""
#from __future__ import unicode_literals
#from __future__ import absolute_import

import sys
import os
import unittest
import responses
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import koordinates

def getpass():
    '''
    Prompt user for Password until there is a Connection object
    '''
    import getpass
    return(getpass.getpass('Please enter your Koordinates password: '))


class TestKoordinates(unittest.TestCase):

    pwd = getpass()


    def setUp(self):
        pass

    def test_layers_url_template(self):
        L = koordinates.api.Layer('rshea@thecubagroup.com', TestKoordinates.pwd, 999)
        assert L.url('GET', 'single') == '''https://koordinates.com/services/api/v1/layers/999/'''


    def test_layers_url_template(self):
        L = koordinates.api.Layer('rshea@thecubagroup.com', TestKoordinates.pwd, 999)
        assert L.url_templates('GET', 'single') == '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''

    @responses.activate
    def test_basic_auth(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                      body='{"error": "not found"}', status=404,
                      content_type='application/json')

        resp = requests.get('http://twitter.com/api/1/foobar')

        assert resp.json() == {"error": "not found"}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://twitter.com/api/1/foobar'
        assert responses.calls[0].response.text == '{"error": "not found"}'

    @responses.activate
    def test_basic_auth_1(self):
        the_url = '''http://httpbin.org/basic-auth/user/passwd'''
        the_response = '''
            {
              "authenticated": true, 
              "user": "user"
            }
        '''
        import json
        the_response = json.dumps({'authenticated':True, 'user':'user'})
        the_response.replace('\'' , '"')

        responses.add(responses.GET, the_url,  
                      body=the_response, status=200,
                      content_type='application/json')

        resp = requests.get(the_url)

        #assert resp.json() == the_response 

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == the_url 
        #assert responses.calls[0].response.text == '{"user": "user"}'
        assert responses.calls[0].response.text == the_response

    @responses.activate
    def test_get_layer_by_id_no_auth(self):
        pass
    @responses.activate
    def test_get_layer_by_id(self, id=1474):

        the_response = '''{"id": 1474, "url": "https://koordinates.com/services/api/v1/layers/1474/", "type": "layer", "name": "Wellington City Building Footprints", "first_published_at": "2010-06-21T05:05:05.953", "published_at": "2012-05-09T02:11:27.020Z", "description": "Polygons representing building rooftop outlines for urban Wellington including Makara Beach and Makara Village. Each building has an associated elevation above MSL (Wellington 1953). The rooftop elevation does not include above roof structures such as aerials or chimneys. Captured in 1996 and updated in 1998, 1999, 2002, 2006, 2009, 2011 and 2012 in conjunction with aerial photography refly projects.", "description_html": "<p>Polygons representing building rooftop outlines for urban Wellington including Makara Beach and Makara Village. Each building has an associated elevation above MSL (Wellington 1953). The rooftop elevation does not include above roof structures such as aerials or chimneys. Captured in 1996 and updated in 1998, 1999, 2002, 2006, 2009, 2011 and 2012 in conjunction with aerial photography refly projects.</p>", "group": {"id": 119, "url": "https://koordinates.com/services/api/v1/groups/119/", "name": "Wellington City Council", "country": "NZ"}, "data": {"encoding": null, "crs": "EPSG:2193", "primary_key_fields": [], "datasources": [{"id": 65935}], "geometry_field": "GEOMETRY", "fields": [{"name": "GEOMETRY", "type": "geometry"}, {"name": "OBJECTID", "type": "integer"}, {"name": "Shape_Leng", "type": "double"}, {"name": "Shape_Area", "type": "double"}, {"name": "elevation", "type": "double"}, {"name": "feat_code", "type": "string"}, {"name": "source", "type": "string"}]}, "url_html": "https://koordinates.com/layer/1474-wellington-city-building-footprints/", "published_version": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/", "latest_version": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/", "this_version": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/", "kind": "vector", "categories": [{"name": "Cadastral & Property", "slug": "cadastral"}], "tags": ["building", "footprint", "outline", "structure"], "collected_at": ["1996-12-31", "2012-05-01"], "created_at": "2010-06-21T05:05:05.953", "license": {"id": 9, "title": "Creative Commons Attribution 3.0 New Zealand", "type": "cc-by", "jurisdiction": "nz", "version": "3.0", "url": "https://koordinates.com/services/api/v1/licenses/9/", "url_html": "https://koordinates.com/license/attribution-3-0-new-zealand/"}, "metadata": {"iso": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/iso/", "dc": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/dc/", "native": "https://koordinates.com/services/api/v1/layers/1474/versions/4067/metadata/"}, "elevation_field": "elevation"}'''

        L = koordinates.api.Layer('rshea@thecubagroup.com', TestKoordinates.pwd, 999)

        responses.add(responses.GET, L.url('GET', 'single', id),  
                      body=the_response, status=200,
                      content_type='application/json')

        L.get(id)
        
        assert L.name == "Wellington City Building Footprints" 

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
 
    def test_stub(self):
        assert len("x") == 1 

    def test_sample(self):
        assert koordinates.sample(2, 5) == 10 

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
