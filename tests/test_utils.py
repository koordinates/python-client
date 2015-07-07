import datetime
import unittest

from koordinates.utils import make_date


class UtilsTest(unittest.TestCase):
    def test_make_date(self):
        self.assertEqual(make_date(""), "")
        self.assertEqual(make_date(None), "")
        self.assertEqual(make_date("2013-01-01"), datetime.datetime(2013, 1, 1, 0, 0))
