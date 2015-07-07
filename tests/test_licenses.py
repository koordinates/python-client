import unittest

import responses

from koordinates import Client, License, ClientValidationError

from response_data.licenses import license_list, license_cc_10
from response_data.responses_5 import layers_version_single_good_simulated_response


class LicenseTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(token='test', host="test.koordinates.com")

    @responses.activate
    def test_list(self):
        responses.add(responses.GET,
                      self.client.get_url('LICENSE', 'GET', 'multi'),
                      body=license_list, status=200,
                      content_type='application/json')

        licenses = list(self.client.licenses.list())

        self.assertEqual(len(licenses), 23)
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_list_cc(self):
        responses.add(responses.GET,
                      self.client.get_url('LICENSE', 'GET', 'cc', {'slug': 'cc-by-nc', 'jurisdiction': ''}),
                      body=license_cc_10, status=200,
                      content_type='application/json')

        responses.add(responses.GET,
                      self.client.get_url('LICENSE', 'GET', 'cc', {'slug': 'cc-by-nc', 'jurisdiction': 'au'}),
                      body=license_cc_10, status=200,
                      content_type='application/json')

        license = self.client.licenses.get_creative_commons('cc-by-nc')
        self.assert_(isinstance(license, License))
        license = self.client.licenses.get_creative_commons('cc-by-nc', 'au')
        self.assert_(isinstance(license, License))

        with self.assertRaises(ClientValidationError):
            self.client.licenses.get_creative_commons('nc', 'au')

        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_get(self):
        responses.add(responses.GET,
                      self.client.get_url('LICENSE', 'GET', 'single', {'id': 10}),
                      body=license_cc_10, status=200,
                      content_type='application/json')

        license = self.client.licenses.get(10)
        self.assert_(isinstance(license, License))
        self.assertEqual(license.id, 10)
        self.assertEqual(license.type, 'cc-by-nd')
        self.assertEqual(license.jurisdiction, 'nz')

        self.assertEqual(str(license), "10 - Creative Commons Attribution-No Derivative Works 3.0 New Zealand")

    @responses.activate
    def test_layer(self):
        responses.add(responses.GET,
                      self.client.get_url('LAYER', 'GET', 'single', {'id': 1474}),
                      body=layers_version_single_good_simulated_response, status=200,
                      content_type='application/json')

        layer = self.client.layers.get(1474)
        self.assert_(isinstance(layer.license, License))

        license = layer.license
        self.assertEqual(license.id, 9)
