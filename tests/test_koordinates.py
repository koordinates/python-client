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
#from requests.exceptions import HTTPError

#from koordinates import koordinates

class TestKoordinates(unittest.TestCase):

    def setUp(self):
        pass


    def test_upper(self):
        '''
        This, obviously, is not a real test but
        rather a placeholder in order to test
        the testing infrastructure
        '''
        self.assertEqual('foo'.upper(), 'FOO')


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
