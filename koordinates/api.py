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

SUPPORTED_API_VERSIONS = ['v1', 'UNITTESTINGONLY']


class Connection(object):
    """
    This is a python library for accessing the koordinates api
    """

    def __init__(self, username, pwd=None, host='koordinates.com', api_version='v1', activate_logging=True):
        if activate_logging:
            client_logfile_name = "koordinates-client-{}.log".format(datetime.now().strftime('%Y%m%dT%H%M%S'))
            logging.basicConfig(filename=client_logfile_name,
                                level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(module)s %(message)s')

        logger.debug('Initializing Connection object')

        if api_version not in SUPPORTED_API_VERSIONS:
            raise koordexceptions.KoordinatesInvalidAPIVersion
        else:
            self.api_version = api_version

        self.host = host

        self.username = username
        if pwd:
            self.pwd = pwd
        else:
            self.pwd = os.environ['KPWD']

        self.layer = Layer(self)
        self.set = Set(self)
        self.version = Version(self)
        self.data = KData(self)

    def get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)


class KoordinatesURLMixin(object):
    def __init__(self):
        self._url_templates = {}
        self._url_templates['LAYER'] = {}
        self._url_templates['LAYER']['GET'] = {}
        self._url_templates['LAYER']['GET']['single'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/'''
        self._url_templates['LAYER']['GET']['multi'] = '''https://{hostname}/services/api/{api_version}/layers/'''
        self._url_templates['SET'] = {}
        self._url_templates['SET']['GET'] = {}
        self._url_templates['SET']['GET']['single'] = '''https://{hostname}/services/api/{api_version}/sets/{set_id}/'''
        self._url_templates['SET']['GET']['multi'] = '''https://{hostname}/services/api/{api_version}/sets/'''
        self._url_templates['VERSION'] = {}
        self._url_templates['VERSION']['GET'] = {}
        self._url_templates['VERSION']['GET']['single'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/{version_id}/'''
        self._url_templates['VERSION']['GET']['multi'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/'''
        self._url_templates['VERSION']['POST'] = {}
        self._url_templates['VERSION']['POST']['import'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/import'''
        self._url_templates['DATA'] = {}
        self._url_templates['DATA']['GET'] = {}
        self._url_templates['DATA']['GET']['multi'] = '''https://{hostname}/services/api/{api_version}/data/'''

    def url_templates(self, datatype, verb, urltype):
        return self._url_templates[datatype][verb][urltype]

    def get_url(self, datatype, verb, urltype, kwargs={}):
        if "hostname" not in kwargs:
            kwargs['hostname'] = self._parent.host
        if "api_version" not in kwargs:
            kwargs['api_version'] = self._parent.api_version

        return self.url_templates(datatype, verb, urltype).format(**kwargs)

    def get_url_TODO_REMOVE(self, datatype, verb, urltype, id=None):
        if id:
            return self.url_templates(datatype, verb, urltype)\
                       .format(hostname=self._parent.host,
                               api_version=self._parent.api_version,
                               layer_id=id)
        else:
            return self.url_templates(datatype, verb, urltype)\
                       .format(hostname=self._parent.host,
                               api_version=self._parent.api_version)


class KoordinatesObjectMixin(object):

    def get(self, id, target_url):
        """Fetches a sing object determined by the value of `id`.

        :param id: ID for the new :class:`Set` object.
        """

        dynamic_build = True 

        self._raw_response = requests.get(target_url,
                                         auth=self._parent.get_auth())

        if self._raw_response.status_code == 200:
            # convert JSON to dict
            dic_json = json.loads(self._raw_response.text)
            # itererte over resulting dict
            if dynamic_build:
                for dict_key, dict_element_value in dic_json.items():
                    if isinstance(dict_element_value, dict):
                        # build dynamically defined class instances (nested
                        # if necessary) in order to model associative arrays
                        att_value = self._class_builder_from_dict(dic_json[dict_key], dict_key)
                    elif isinstance(dict_element_value, list):
                        att_value = self.__class_builder_from_sequence(dic_json[dict_key])
                    elif isinstance(dict_element_value, tuple):
                        # Don't believe the json.loads will ever create Tuples and supporting
                        # them later is costly so for the moment we just give up at this point
                        raise NotImplementedError("JSON that creates Tuples is not currently supported")
                    else:
                        # Allocate value to attribute directly
                        att_value = dict_element_value
                    self.__create_attribute(dict_key, att_value)
            else:
                raise NotImplementedError

        elif self._raw_response.status_code == 404:
            raise koordexceptions.KoordinatesInvalidURL
        elif self._raw_response.status_code == 401:
            raise koordexceptions.KoordinatesNotAuthorised
        elif self._raw_response.status_code == 429:
            raise koordexceptions.KoordinatesRateLimitExceeded
        elif self._raw_response.status_code == 504:
            raise koordexceptions.KoordinatesServerTimeOut
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse

    def filter(self, value):
        if self._filtering_applied:
            raise koordexceptions.KoordinatesOnlyOneFilterAllowed

        # Eventually this check will be a good deal more sophisticated
        # so it's here in its current form to some degree as a placeholder
        if value.isspace():
            raise koordexceptions.KoordinatesFilterMustNotBeSpaces()

        self.add_query_component("q", value)
        self._filtering_applied = True
        return self

    def order_by(self, sort_key):
        if self._ordering_applied:
            raise koordexceptions.KoordinatesOnlyOneOrderingAllowed
        if sort_key not in self._attribute_sort_candidates:
            raise koordexceptions.KoordinatesNotAValidBasisForOrdering(sort_key)

        self.add_query_component("sort", sort_key)
        self._ordering_applied = True
        return self

    def add_query_component(self, argname, argvalue):

        # parse original string url
        url_data = urlsplit(self._url)

        # parse original query-string
        qs_data = parse_qs(url_data.query)

        # manipulate the query-string
        qs_data[argname] = [argvalue]

        # get the url with modified query-string
        self._url = url_data._replace(query=urlencode(qs_data, True)).geturl()

    def execute_get_list(self):
        self.__execute_get_list_no_generator()
        for response in self._list_of_response_dicts:
            this_object = self.__class__(self._parent)
            for key, value in response.items():
                setattr(this_object, key, value)
            yield this_object

    def __execute_get_list_no_generator(self):

        target_url = self._url
        self._url = ""
        self._ordering_applied = False
        self._filtering_applied = False
        self._raw_response = requests.get(target_url,
                                         auth=self._parent.get_auth())

        if self._raw_response.status_code == 200:
            self._list_of_response_dicts = self._raw_response.json()
        elif self._raw_response.status_code == 404:
            self._list_of_response_dicts = self._raw_response.json()
            raise koordexceptions.KoordinatesInvalidURL
        elif self._raw_response.status_code == 401:
            self._list_of_response_dicts = self._raw_response.json()
            raise koordexceptions.KoordinatesNotAuthorised
        elif self._raw_response.status_code == 429:
            self._list_of_response_dicts = self._raw_response.json()
            raise koordexceptions.KoordinatesRateLimitExceeded
        elif self._raw_response.status_code == 504:
            self._list_of_response_dicts = self._raw_response.json()
            raise koordexceptions.KoordinatesServerTimeOut
        else:
            self.list_oflayer_dicts = self._raw_response.json()
            raise koordexceptions.KoordinatesUnexpectedServerResponse

    def __create_attribute(self, att_name, att_value):
        if att_name in self._attribute_reserved_names:
            errmsg = """The name '{attname}' is not able to be used """ \
                     """an attribute name for the class '{classname}' """ \
                     """as it appears in the '_attribute_reserved_names' """ \
                     """list""".format(attname=att_name, classname=type(self).__name__)
            raise koordexceptions.KoordinatesAttributeNameIsReserved(errmsg)

        if isinstance(att_value, list):
            att_value = [self.__make_date_if_possible(v) for v in att_value]
        else:
            att_value = self.__make_date_if_possible(att_value)

        setattr(self, att_name, att_value)

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
                seq_out.append(self._class_builder_from_dict(seq_element, str(uuid.uuid1())))
            else:
                seq_out.append(self.__make_date_if_possible(seq_element))
        return seq_out

    def _class_builder_from_dict(self, the_dic, the_name):
        '''_class_builder_from_dict supports the dynamic creation of
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
                dic_out[dict_key] = self._class_builder_from_dict(dict_key_value, dict_key)
            if isinstance(dict_key_value, list) or isinstance(dict_key_value, tuple):
                dic_out[dict_key] = self.__class_builder_from_sequence(dict_key_value)
            else:
                dic_out[dict_key] = self.__make_date_if_possible(dict_key_value)
        return type(str(the_name.title()), (object,), dic_out)


class KData(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Data

    TODO: Description of what a `Data` is

    '''
    def __init__(self, parent, id=None):
        logger.info('Initializing Data object')
        self._parent = parent
        self._url = None
        self._id = id

        self._raw_response = None
        self._list_of_response_dicts = []
        self._attribute_sort_candidates = ['name']
        self._attribute_filter_candidates = ['name']
        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names
        self._attribute_reserved_names = []
        super(self.__class__, self).__init__()

    def get_list(self):
        """Fetches a set of sets
        """
        target_url = self.get_url('DATA', 'GET', 'multi')
        self._url = target_url
        return self


class Set(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Set

    TODO: Description of what a `Set` is

    '''
    def __init__(self, parent, id=None):
        logger.info('Initializing Set object')
        self._parent = parent
        self._url = None
        self._id = id

        self._raw_response = None
        self._list_of_response_dicts = []
        self._attribute_sort_candidates = ['name']
        self._attribute_filter_candidates = ['name']
        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names
        self._attribute_reserved_names = []
        super(self.__class__, self).__init__()

    def get_list(self):
        """Fetches a set of sets
        """
        target_url = self.get_url('SET', 'GET', 'multi')
        self._url = target_url
        return self

    def get(self, id):
        """Fetches a Set determined by the value of `id`.

        :param id: ID for the new :class:`Set` object.
        """

        target_url = self.get_url('SET', 'GET', 'single', {'set_id': id})
        super(self.__class__, self).get(id, target_url)


class Version(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Version
    TODO: Explanation of what a `Version` is from Koordinates
    '''
    def __init__(self, parent, id=None):
        logger.info('Initializing Version object')
        self._parent = parent
        self._url = None

        self._raw_response = None
        self._list_of_response_dicts = []

        self._ordering_applied = False
        self._filtering_applied = False
        self._attribute_sort_candidates = ['name']
        self._attribute_filter_candidates = ['name']

        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names
        self._attribute_reserved_names = []

        super(self.__class__, self).__init__()

    def get_list(self, layer_id):
        """Fetches a set of layers
        """
        target_url = self.get_url('VERSION', 'GET', 'multi', {'layer_id': layer_id})
        self._url = target_url
        return self

    def get(self, layer_id, version_id):
        """Fetches a version determined by the value of `version_id`.

        :param id: ID for the new :class:`Version` object.
        """

        raise NotImplementedError

    def import_version(self, layer_id):
        """Reimport an existing layer from its previous datasources
        and create a new version
        """
        target_url = self.get_url('VERSION', 'POST', 'import', {'layer_id': id})
        test_auth=self._parent.get_auth()
        self._raw_response = requests.get(target_url,
                                          auth=self._parent.get_auth())
        if self._raw_response.status_code == 202:
            # Success ! Update accepted for Processing but not 
            # necesarily complete
            pass
        elif self._raw_response.status_code == 409:
            # Indicates that the request could not be processed because 
            # of conflict in the request, such as an edit conflict in 
            # the case of multiple updates
            raise KoordinatesImportEncounteredUpdateConflict
        elif self._raw_response.status_code == 404:
            # The resource specificed in the URL could not be found
            raise koordexceptions.KoordinatesInvalidURL
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse


class Group(object):
    def __init__(self, id=None, url=None, name=None, country=None):
        self.id = id
        self.url = url
        self.name = name
        self.country = country

class Data(object):
    def __init__(self, encoding=None, crs=None,
                 primary_key_fields=[],
                 datasources=[],
                 geometry_field=None,
                 fields=[]):

        assert type(primary_key_fields) is list,\
                "The 'Data' attribute 'primary_key_fields' must be a list"
        assert type(datasources) is list,\
            "The 'Data' attribute 'datasources' must be a list"
        assert type(fields) is list,\
            "The 'Data' attribute 'fields' must be a list"
        assert all(isinstance(ds_instance, DataSource) for ds_instance in datasources),\
            "The 'Data' attribute 'datasources' must be a list of DataSource objects"
        assert all(isinstance(ds_instance, Field) for f_instance in fields),\
            "The 'Data' attribute 'datasources' must be a list of DataSource objects"

        self.encoding = encoding 
        self.crs = crs
        self.primary_key_fields = primary_key_fields
        self.primary_key_fields = primary_key_fields
        self.datasources = datasources
        self.geometry_field = geometry_field
        self.fields = fields

class DataSource(object):
    def __init__(self, id):
        self.id = id

class Category(object):
    def __init__(self, name, slug):
        self.name = name 
        self.slug = slug 

class License(object):
    def __init__(self, 
                 id=None,
                 title=None ,
                 type=None,
                 jurisdiction=None ,
                 version=None ,
                 url=None ,
                 url_html=None ):

        self.id = id 
        self.title = title 
        self.type = type 
        self.jurisdiction = jurisdiction 
        self.version = version 
        self.url = url 
        self.url_html = url_html 

class Metadata(object):
    def __init__(self, iso=None, dc=None, native=None):
        self.iso = iso
        self.dc = dc 
        self.native = native
    
class Field(object):
    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type

class Layer(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items,
    but are manipulated as a single unit. Layers generally reflect collections
    of objects that you add on top of the map to designate a common
    association.
    '''
    def __init__(self, 
                 parent=None, 
                 id=None,
                 url=None,
                 type=None,
                 name=None,
                 first_published_at=None,
                 published_at=None,
                 description=None,
                 description_html=None,
                 group=None,
                 data=None,
                 url_html=None,
                 published_version=None,
                 latest_version=None,
                 this_version=None,
                 kind=None, 
                 categories=None,
                 tags=None,
                 collected_at=None,
                 created_at=None,
                 license=None,
                 metadata=None,
                 elevation_field=None):


        self._parent = parent
        self._url = None
        self._id = id
        self._ordering_applied = False
        self._filtering_applied = False

        self._raw_response = None
        self._list_of_response_dicts = []

        self._attribute_sort_candidates = ['name']
        self._attribute_filter_candidates = ['name']

        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names
        self._attribute_reserved_names = ['version']

        self.id = id
        self.url = url
        self.type = type
        self.name = name
        self.first_published_at = first_published_at
        self.published_at = published_at
        self.description = description
        self.description_html = description_html
        self.group = group if group else Group()
        self.data = data if data else Data()
        self.url_html = url_html
        self.published_version = published_version
        self.latest_version = latest_version
        self.this_version = this_version
        self.kind  = kind
        self.categories = categories if categories else []
        self.tags = tags if tags else []
        self.collected_at = collected_at
        self.created_at = created_at
        self.license = license if license else License()
        self.metadata = metadata if metadata else  Metadata()
        self.elevation_field = elevation_field

        super(self.__class__, self).__init__()

    @classmethod
    def fromjson(cls, datadict):
        '''Initialize Layer from a JSON blob
        
        la = Layer.fromjson(my_json)
        
        '''
            #return cls(datadict.items())


    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('LAYER', 'GET', 'multi')
        self._url = target_url
        return self

    def get(self, id):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """

        target_url = self.get_url('LAYER', 'GET', 'single', {'layer_id': id})
        super(self.__class__, self).get(id, target_url)


def sample(foo, bar):
    """Is a Sample for testing purposes.
        :param foo: A sample integer
        :param bar: Another sample integer
    """

    return foo * bar
