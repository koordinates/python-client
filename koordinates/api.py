# -*- coding: utf-8 -*-

"""
koordinates.api
~~~~~~~~~~~~
This module implements the Koordinates API.

:copyright: (c) 2015 by Koordinates .
:license: BSD, see LICENSE for more details.
"""

import os
import requests
import json
import uuid
from datetime import datetime
try:
        # from urllib.parse import urlparse
        from urllib.parse import urlencode
        from urllib.parse import urlsplit
        from urllib.parse import parse_qs
except ImportError:
        # from urlparse import urlparse
        from urllib import urlencode
        from urlparse import urlsplit
        from urlparse import parse_qs

import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path


import logging
logger = logging.getLogger(__name__)

import dateutil.parser

import koordexceptions


class Connection(object):
    """
    This is a python library for accessing the koordinates api
    """

    def __init__(self, username, pwd=None, host='koordinates.com', activate_logging=True):
        if activate_logging:
            #d=datetime.now()
            client_logfile_name = "koordinates-client-{}.log".format(datetime.now().strftime('%Y%m%dT%H%M%S'))
            #client_logfile_name = "koordinates-client-{}.log".format(d=datetime.now().strftime('%Y%m%dT%H%M%S'))

            logging.basicConfig(filename=client_logfile_name,
                                level=logging.DEBUG, 
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('!!!! DONT FORGET LOGGING DEFAULTS TO TRUE. NEEDS CHANGING BEFORE 1.x.x  !!!!')
        logger.debug('Initializing Connection object')
        self.username = username
        if pwd:
            self.pwd = pwd
        else:
            self.pwd = os.environ['KPWD']
        self.host = host
        self.layer = Layer(self)
        self.set = Set(self)

    def get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)


class KoordinatesURLMixin(object):
    def __init__(self):
        self._url_templates = {}
        self._url_templates['LAYER'] = {}
        self._url_templates['LAYER'] ['GET'] = {}
        self._url_templates['LAYER'] ['GET']['single'] = '''https://{hostname}/services/api/v1/layers/{layer_id}/'''
        self._url_templates['LAYER'] ['GET']['multi'] = '''https://{hostname}/services/api/v1/layers/'''
        self._url_templates['SET'] = {}
        self._url_templates['SET'] ['GET'] = {}
        self._url_templates['SET'] ['GET']['single'] = '''https://{hostname}/services/api/v1/sets/{layer_id}/'''
        self._url_templates['SET'] ['GET']['multi'] = '''https://{hostname}/services/api/v1/sets/'''

    def url_templates(self, datatype, verb, urltype):
        return self._url_templates[datatype][verb][urltype]

    def get_url(self, datatype, verb, urltype, id=None):
        if id:
            return self.url_templates(datatype, verb, urltype)\
                    .format(hostname=self.parent.host, layer_id=id)
        else:
            return self.url_templates(datatype, verb, urltype)\
                    .format(hostname=self.parent.host)


class KoordinatesObjectMixin(object):

    def get(self, id, target_url):
        """Fetches a sing object determined by the value of `id`.

        :param id: ID for the new :class:`Set` object.
        """

        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code == 200:
            # convert JSON to dict
            dic_json = json.loads(self.raw_response.text)
            # itererte over resulting dict
            for dict_key, dict_element_value in dic_json.items():
                if isinstance(dict_element_value, dict):
                    # build dynamically defined class instances (nested
                    # if necessary) in order to model associative arrays
                    att_value = self.__class_builder(dic_json[dict_key], dict_key)
                elif isinstance(dict_element_value, list) or isinstance(dict_element_value, tuple):
                    att_value = self.__class_builder_from_sequence(dic_json[dict_key])
                else:
                    #Allocate value to attribute directly
                    att_value = self.__make_date_if_possible(dict_element_value)
                setattr(self, dict_key, att_value)
        elif self.raw_response.status_code == 404:
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code == 401:
            raise koordexceptions.KoordinatesNotAuthorised
        elif self.raw_response.status_code == 429:
            raise koordexceptions.KoordinatesRateLimitExceeded
        elif self.raw_response.status_code == 504:
            raise koordexceptions.KoordinatesServerTimeOut
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse

    def execute_get_list(self):
        import copy
        self.__execute_get_list_no_generator()
        for response in self.list_of_response_dicts:
            this_object = self.__class__(self.parent)
            for key, value in response.items():
                setattr(this_object, key, value)
            yield this_object


    def __make_date_if_possible(self, value):
        '''
        Try convering the value to a date
        and if that doesn't work then just 
        return the value was it was passed 
        in.
        '''
        try:
            out = dateutil.parser.parse(value) 
        except ValueError:
            out = value
        except AttributeError:
            out = value

        return out

    def __execute_get_list_no_generator(self):

        target_url = self.url
        self.url = ""
        self.ordering_applied = False
        self.filtering_applied = False
        self.raw_response = requests.get(target_url,
                                         auth=self.parent.get_auth())

        if self.raw_response.status_code == 200:
            self.list_of_response_dicts = self.raw_response.json()
        elif self.raw_response.status_code == 404:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesInvalidURL
        elif self.raw_response.status_code == 401:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesNotAuthorised
        elif self.raw_response.status_code == 429:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesRateLimitExceeded
        elif self.raw_response.status_code == 504:
            self.list_of_response_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesServerTimeOut
        else:
            self.list_oflayer_dicts = self.raw_response.json()
            raise koordexceptions.KoordinatesUnexpectedServerResponse

    def filter(self, value):
        if self.filtering_applied:
            raise koordexceptions.KoordinatesOnlyOneFilterAllowed

        # Eventually this check will be a good deal more sophisticated
        # so it's here in its current form to some degree as a placeholder
        if value.isspace():
            raise koordexceptions.KoordinatesFilterMustNotBeSpaces()

        self.add_query_component("q", value)
        self.filtering_applied = True
        return self

    def order_by(self, sort_key):
        if self.ordering_applied:
            raise koordexceptions.KoordinatesOnlyOneOrderingAllowed
        if sort_key not in self.attribute_sort_candidates:
            raise koordexceptions.KoordinatesNotAValidBasisForOrdering(sort_key)

        self.add_query_component("sort", sort_key)
        self.ordering_applied = True
        return self

    def add_query_component(self, argname, argvalue):

        # parse original string url
        url_data = urlsplit(self.url)

        # parse original query-string
        qs_data = parse_qs(url_data.query)

        # manipulate the query-string
        qs_data[argname] = [argvalue]

        # get the url with modified query-string
        self.url = url_data._replace(query=urlencode(qs_data, True)).geturl()

    def __class_builder_from_sequence(self, the_seq):
        '''__class_builder supports the dynamic creation of 
        object attributes in response to JSON returned from the 
        server. 

        Where a JSON blob returned from the server (itself an
        associative array) includes nested associative arrays
        we need to create a class that corresponds to the contents
        of that array, create an instance of the class and then 
        make that instance an attribute of our container class,
        for instance, a Layer
        '''
        seq_out = []
        for seq_element in the_seq:
            if isinstance(seq_element, list) or isinstance(seq_element, tuple):
                seq_out.append(self.__class_builder_from_sequence(seq_element)) 
            elif isinstance(seq_element, dict):
                seq_out.append(self.__class_builder(seq_element,str(uuid.uuid1())))
            else:
                seq_out.append(self.__make_date_if_possible(seq_element))
        return seq_out

    def __class_builder(self, the_dic, the_name):
        '''__class_builder supports the dynamic creation of 
        object attributes in response to JSON returned from the 
        server. 

        Where a JSON blob returned from the server (itself an
        associative array) includes nested associative arrays
        we need to create a class that corresponds to the contents
        of that array, create an instance of the class and then 
        make that instance an attribute of our container class,
        for instance, a Layer
        '''
        dic_out = {}
        for dict_key, dict_key_value in the_dic.items():
            if isinstance(dict_key_value, dict):
                dic_out[dict_key] = self.__class_builder(dict_key_value, dict_key) 
            if isinstance(dict_key_value, list) or isinstance(dict_key_value, tuple):
                dic_out[dict_key] = self.__class_builder_from_sequence(dict_key_value) 
            else:
                dic_out[dict_key] = self.__make_date_if_possible(dict_key_value) 
        return type(str(the_name.title()), (object,), dic_out)

class Set(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Set  

    TODO: Description of what a `Set` is

    '''
    def __init__(self, parent, id=None):
        logger.info('Initializaing Set object')
        self.parent = parent
        self.url = None
        self._id = id
        self.list_of_response_dicts = []
        self.attribute_sort_candidates = ['name']
        self.attribute_filter_candidates = ['name']
        super(self.__class__, self).__init__()

    def get_list(self):
        """Fetches a set of sets  
        """
        target_url = self.get_url('SET', 'GET', 'multi', None)
        self.url = target_url
        return self

    def get(self, id):
        """Fetches a Set determined by the value of `id`.

        :param id: ID for the new :class:`Set` object.
        """

        target_url = self.get_url('SET', 'GET', 'single', id)
        super(self.__class__, self).get(id, target_url)

class Layer(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items,
    but are manipulated as a single unit. Layers generally reflect collections
    of objects that you add on top of the map to designate a common
    association.
    '''
    def __init__(self, parent, id=None,
                 layer_name=None,
                 layer_type=None,
                 first_published_at=None,
                 published_at=None):

        self.parent = parent
        self.url = None
        self._id = id
        self.name = layer_name
        self._type = layer_type
        self._first_published_at = first_published_at
        self.cg_published_at = published_at
        self.ordering_applied = False
        self.filtering_applied = False

        self.raw_response = None
        self.list_of_response_dicts = []

        self.attribute_sort_candidates = ['name']
        self.attribute_filter_candidates = ['name']

        super(self.__class__, self).__init__()


    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('LAYER', 'GET', 'multi', None)
        self.url = target_url
        return self

    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """

        target_url = self.get_url('LAYER', 'GET', 'single', id)
        super(self.__class__, self).get(id, target_url)


def sample(foo, bar):
    """Is a Sample for testing purposes.
        :param foo: A sample integer
        :param bar: Another sample integer
    """

    return foo * bar
