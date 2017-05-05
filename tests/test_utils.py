import datetime

from koordinates.utils import make_date


def test_make_date():
    assert make_date("") == ""
    assert make_date(None) == ""
    assert make_date("2013-01-01") == datetime.datetime(2013, 1, 1, 0, 0)
