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
    Decorator that asserts the model instance is bound (ie. has an ID and a manager set)
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._is_bound:
            raise ValueError("%r must be bound to call %s" % (self, method.__name__))
        return method(self, *args, **kwargs)
    return wrapper


def is_empty_list(candidate_list):
    '''
    Determines if the list passed as an argumenent is either
    a list or a tuple and is empty

    :param candidate_list: a list to inspect.
    :return: boolean
    '''
    ret_value = False
    if isinstance(candidate_list, list) or isinstance(candidate_list, tuple):
        if len(candidate_list) == 0:
            ret_value = True

    return ret_value

def remove_empty_from_dict(d):
    '''
    Given a, potentially, complex dictionary another dictionary
    is returned with all those parts which contained no data
    removed from it

    :param d: a list to inspect.
    :return: dict
    '''
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

def dump_class_attributes_to_dict(obj, path=[], dic_out={},
                                  root=None, skip_underbars = True,
                                  ignore_nones = False):
    '''
    Given an object instance which, potentially, contains a complex
    heirarchy of other class instances, some of which may be lists
    of class instances, a dictionary is returned containing the
    value of the instance attributes keyed on the original
    attribute names.

    The structure of the resulting dictionary emulates that of the
    instance heirarchy

    NB: This function is recursive.

    :param obj: a instance on which to operate
    :param path: a list of key names traversed to get to the current point of processing
    :param dic_out: a dictionary containing the current state of the dictionary which\
            will eventually be returned
    :param root: TODO - remove this argument as it is redundant
    :param skip_underbars: When True then all attributes which have a name beginning\
            to with an underbar are ignored for the purposes of the output. This also\
            means that attributes within 'underbarred' attributes are ignored regardless\
            of their name.
    :param ignore_nones: TODO - remove this argument as it is redundant

    :return: dict

    '''

    for attr_name, attr_value in obj.__dict__.items():
        if skip_underbars and attr_name[0] == "_":
            pass
        elif ignore_nones and attr_value is None:
            pass
        elif ignore_nones and is_empty_list(attr_value):
            pass
        elif ignore_nones and (isinstance(attr_value, list) or isinstance(attr_value, tuple)):
            pass
        else:
            if hasattr(attr_value, '__dict__'):
                path.append(attr_name)
                dic_out[attr_name]={}
                dump_class_attributes_to_dict(attr_value,
                                              path,
                                              dic_out[attr_name])
            else:
                if isinstance(attr_value, list) or isinstance(attr_value, tuple):
                    lst_dumps = []
                    dic_out[attr_name]={}
                    for attr_element in attr_value:
                        attr_element_as_json = dump_class_attributes_to_dict(attr_element,
                                                                             path,
                                                                             dic_out[attr_name])
                        lst_dumps.append(attr_element_as_json)
                    dic_out[attr_name] = lst_dumps
                else:
                    # +++++++++++++++++++++++++++++++++++++++++
                    # The variable strpath is for
                    # diagnostic use only
                    strpath = ".".join(path)
                    if strpath:
                        dotornot = "."
                    else:
                        dotornot = ""
                    strpath = strpath + dotornot + attr_name
                    # +++++++++++++++++++++++++++++++++++++++++
                    dic_out[attr_name] = attr_value
    if path:
        path.pop()

    return dic_out

def make_date_list_from_string_list(listin):
    '''Returns a `DateTime` object, if `v` is a populated string, or an empty string.

    :param v: either a string parseable as a date/time; an empty string; or None
    :return either a `DateTime` corresponding to `v` or an empty String

    '''
    lstout = []
    if listin:
        for listin_elem in listin:
            lstout.append(dateutil.parser.parse(listin_elem))

    return lstout

def make_date(v):
    '''Returns a `DateTime` object, if `v` is a populated string, or an empty string.

    :param v: either a string parseable as a date/time; an empty string; or None
    :return either a `DateTime` corresponding to `v` or an empty String

    '''
    if v == "" or v is None:
        return ""
    else:
        return dateutil.parser.parse(v)


def make_date_if_possible(value):
    '''
    Try converting the value to a date
    and if that doesn't work then just
    return the value was it was passed
    in.

    :param value: a value which may be a string parseable as a date

    :return: either a DateTime instance or whatever was passed in `value`.
    '''
    try:
        out = dateutil.parser.parse(value)
    except ValueError:
        out = value
    except AttributeError:
        out = value

    return out
