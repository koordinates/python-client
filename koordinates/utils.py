# -*- coding: utf-8 -*-

"""
koordinates.utils
~~~~~~~~~~~~~~

This module provides utility functions and classes used in the Koordinates
Client Library

"""
import functools

import dateutil.parser


def is_bound(method):
    """
    Decorator that asserts the model instance is bound.

    Requires:
    1. an ``id`` attribute
    2. a ``url`` attribute
    2. a manager set
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._is_bound:
            raise ValueError("%r must be bound to call %s()" % (self, method.__name__))
        return method(self, *args, **kwargs)
    return wrapper


def make_date(v):
    '''Returns a `DateTime` object, if `v` is a populated string, or an empty string.

    :param v: either a string parseable as a date/time; an empty string; or None
    :return either a `DateTime` corresponding to `v` or an empty String

    '''
    if v == "" or v is None:
        return ""
    else:
        return dateutil.parser.parse(v)
