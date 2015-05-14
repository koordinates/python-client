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
import sys
sys.path.append('/home/rshea/dev/koordinates-python-client/python-client')
#from koordinates import koordinates
import koordinates

class TestKoordinates(unittest.TestCase):

    def setUp(self):
        pass


    def test_sample(self):
        '''
        A fake test to test koordinates.sample
        '''
        #self.assertEqual(koordinates.sample(5,2) 10)
        self.assertEqual(10, 10)
        
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
