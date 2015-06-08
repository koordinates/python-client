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


class KoordinatesURLMixin(object):
    def __init__(self):
        self._url_templates = {}
        self._url_templates['CONN'] = {}
        self._url_templates['CONN']['POST'] = {}
        self._url_templates['CONN']['POST']['publishmulti'] = '''https://{hostname}/services/api/{api_version}/publish/'''
        self._url_templates['LAYER'] = {}
        self._url_templates['LAYER']['GET'] = {}
        self._url_templates['LAYER']['GET']['singleversion'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/{version_id}/'''
        self._url_templates['LAYER']['GET']['single'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/'''
        self._url_templates['LAYER']['GET']['multi'] = '''https://{hostname}/services/api/{api_version}/layers/'''
        self._url_templates['LAYER']['POST'] = {}
        self._url_templates['LAYER']['POST']['publish'] = '''https://{hostname}/services/api/{api_version}/layers/{layer_id}/versions/{version_id}/publish/'''
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
        self._url_templates['TABLE'] = {}
        self._url_templates['TABLE']['GET'] = {}
        self._url_templates['TABLE']['GET']['singleversion'] = '''https://{hostname}/services/api/{api_version}/tables/{table_id}/versions/{version_id}/'''

    def url_templates(self, datatype, verb, urltype):
        return self._url_templates[datatype][verb][urltype]

    def get_url(self, datatype, verb, urltype, kwargs={}):
        if "hostname" not in kwargs:
            try:
                kwargs['hostname'] = self._parent.host
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Connection`
                # object itself
                kwargs['hostname'] = self.host
        if "api_version" not in kwargs:
            try:
                kwargs['api_version'] = self._parent.api_version
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Connection`
                # object itself
                kwargs['api_version'] = self.api_version

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

    def __specify_page(self, value):
        pass

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
        self._list_of_response_dicts = []
        self._next_page_number = 1
        self.add_query_component("page", self._next_page_number)
        self.__execute_get_list_no_generator()
        for list_of_responses in self._list_of_response_dicts:
            for response in list_of_responses:
                this_object = self.__class__(self._parent)
                for key, value in response.items():
                    setattr(this_object, key, value)
                yield this_object
            if self._link_to_next_in_list:
                self.__execute_get_list_no_generator(target_url=self._link_to_next_in_list)

    def __execute_get_list_no_generator(self,
                                        target_url=None):

        if not target_url:
            target_url = self._url
        self._url = ""
        self._ordering_applied = False
        self._filtering_applied = False
        self._raw_response = requests.get(target_url,
                                          auth=self._parent.get_auth())

        if self._raw_response.status_code == 200:
            self._list_of_response_dicts.append(self._raw_response.json())
            if 'page-next' in self._raw_response.links:
                self._link_to_next_in_list = self._raw_response.links['page-next']['url']
            else:
                self._link_to_next_in_list = None
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


class PublishRequest(KoordinatesURLMixin):
    """
    Defines the nature of a multiple item Publish request
    """
    def __init__(self, layers=[], tables=[], kwargs={}):
        """
        `layers`: a list of dicts of the form {'layer_id':n, 'version_id':m}
        `tables`: a list of dicts of the form {'table_id':n, 'version_id':m}
        """

        assert type(layers) is list,\
            "The 'layers' argument must be a list"
        assert type(tables) is list,\
            "The 'tables' argument must be a list"

        self.layers = layers
        self.tables = tables
        if "hostname" in kwargs:
            self.hostname = kwargs['hostname']
        else:
            self.hostname = None
        if "api_version" in kwargs:
            self.api_version = kwargs['api_version']
        else:
            self.api_version = None

    def add_table_to_publish(self, table_id, version_id):
        self.tables.append({'table_id': table_id, 'version_id': version_id})

    def add_layer_to_publish(self, layer_id, version_id):
        self.layers.append({'layer_id': layer_id, 'version_id': version_id})

    def validate(self):
        '''
        Validates that the resources specified for Publication are in the
        correct format.
        '''

        self.good_layers()
        self.good_tables()

    def good_tables(self):
        '''
        Validates a list of tables ids and a corresponding version id which will be
        used to specify the tables to be published
        '''
        return self.__good_resource_specifications(self.tables, 'table')

    def good_layers(self):
        '''
        Validates a list of layers ids and a corresponding version id which will be
        used to specify the layers to be published
        '''
        return self.__good_resource_specifications(self.layers, 'layer')

    def __good_resource_specifications(self, lst_resources, resource_name):
        '''
        Validates a list of resource ids which will be used to specify the resources
        to be published

        `lst_resource`: A list of dictionaries which correspond to the resources
                        to be published. Each dictionary must have the keys: X_id
                        (where 'X' is 'table', 'layer', etc) ; and 'version_id'.
                        The associated elements should the unique identifiers of
                        the table/version or layer/version which is to be published

        `resource_name`: A string which corresponds to the attribute of this class
                        which is being validated. Valid values are 'layers' and 'tables'

        '''

        if type(lst_resources) is list:
            if len(lst_resources) == 0:
                pass
            else:
                for resource_dict in lst_resources:
                    if type(resource_dict) is dict:
                        if (resource_name + '_id') in resource_dict and 'version_id' in resource_dict:
                            pass
                        else:
                            raise koordexceptions.KoordinatesInvalidPublicationResourceList(
                                "{resname} must be list of dicts. "
                                "Each dict must have the keys "
                                "{resname}_id and version_id".format(resname=resource_name))
                    else:
                        raise koordexceptions.KoordinatesInvalidPublicationResourceList(
                            "Each element of {resname} must be a dict. "
                            .format(resname=resource_name))
        else:
            raise koordexceptions.KoordinatesInvalidPublicationResourceList(
                "{resname} must be list of dicts. "
                "Each dict must have the keys "
                "{resname}_id and version_id".format(resname=resource_name))


class Connection(KoordinatesURLMixin):
    """
    This is a python library for accessing the koordinates api
    """

    def __init__(self, username, pwd=None, host='koordinates.com', 
                 api_version='v1', activate_logging=True):
        if activate_logging:
            client_logfile_name = "koordinates-client-{}.log"\
                                  .format(datetime.now().strftime('%Y%m%dT%H%M%S'))
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

        parent = self
        super(self.__class__, self).__init__()

    def get_auth(self):
        """Creates an Authorisation object
        """
        return requests.auth.HTTPBasicAuth(self.username,
                                           self.pwd)

    def build_multi_publish_json(self, pub_request, publish_strategy, error_strategy):
        '''
        Build a JSON body suitable for the multi-resource
        publishing
        '''

        pub_request.validate()

        dic_out = {}
        if publish_strategy:
            dic_out['publish_strategy'] = publish_strategy
        if error_strategy:
            dic_out['error_strategy'] = error_strategy

        lst_items = []

        for table_resource_dict in pub_request.tables:
            table_resource_dict['hostname'] = self.host
            table_resource_dict['api_version'] = self.api_version
            target_url = self.get_url('TABLE', 'GET', 'singleversion', table_resource_dict)
            lst_items.append(target_url)

        for layer_resource_dict in pub_request.layers:
            layer_resource_dict['hostname'] = self.host
            layer_resource_dict['api_version'] = self.api_version
            target_url = self.get_url('LAYER', 'GET', 'singleversion', layer_resource_dict)
            lst_items.append(target_url)

        dic_out['items'] = lst_items

        return dic_out

    def publish(self, pub_request, publish_strategy=None, error_strategy=None):
        """Publishes a set of items, potentially a mixture of Layers and Tables

        `pub_request`: A `PublishRequest' object specifying what resources are to be published
        `publish_strategy`: One of: `"individual"`, `"together"`. Default = `"together"`
        `error_strategy`: One of: `"abort"`, `"ignore"`. Default = `"abort"`

        """
        assert type(pub_request) is PublishRequest,\
            "The 'items' argument must be a list"
        assert publish_strategy in ["individual", "together", None],\
            "The 'publish_strategy' value must be None or 'individual' or 'together'"
        assert error_strategy in ["abort", "ignore", None],\
            "The 'error_strategy' value must be None or 'abort' or 'ignore'"

        dic_args = {}
        if pub_request.hostname:
            dic_args = {'hostname': pub_request.hostname}
        if pub_request.api_version:
            dic_args = {'api_version': pub_request.api_version}

        target_url = self.get_url('CONN', 'POST', 'publishmulti', dic_args)
        json_headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        dic_body = self.build_multi_publish_json(pub_request, publish_strategy, error_strategy)
        self._raw_response = requests.post(target_url,
                                           json=dic_body,
                                           headers=json_headers,
                                           auth=self.get_auth())

        if self._raw_response.status_code == 201:
            # Success !
            pass
        elif self._raw_response.status_code == 409:
            # Indicates that the request could not be processed because
            # of conflict in the request, such as an edit conflict in
            # the case of multiple updates
            raise koordexceptions.KoordinatesImportEncounteredUpdateConflict
        elif self._raw_response.status_code == 404:
            # The resource specificed in the URL could not be found
            raise koordexceptions.KoordinatesInvalidURL
        else:
            raise koordexceptions.KoordinatesUnexpectedServerResponse


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
        self._link_to_next_in_list = ""
        self._next_page_number = 1
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
        self._link_to_next_in_list = ""
        self._next_page_number = 1
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
        self._link_to_next_in_list = ""
        self._next_page_number = 1

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

    def publish(self, layer_id):
        """Publish the current Version
        """

    def import_version(self, layer_id):
        """Reimport an existing layer from its previous datasources
        and create a new version
        """
        target_url = self.get_url('VERSION', 'POST', 'import', {'layer_id': id})
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
            raise koordexceptions.KoordinatesImportEncounteredUpdateConflict
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
        assert all(isinstance(f_instance, Field) for f_instance in fields),\
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
                 title=None,
                 type=None,
                 jurisdiction=None,
                 version=None,
                 url=None,
                 url_html=None):

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
        self._link_to_next_in_list = ""
        self._next_page_number = 1

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
        self.kind = kind
        self.categories = categories if categories else []
        self.tags = tags if tags else []
        self.collected_at = collected_at
        self.created_at = created_at
        self.license = license if license else License()
        self.metadata = metadata if metadata else Metadata()
        self.elevation_field = elevation_field

        super(self.__class__, self).__init__()

    @classmethod
    def fromjson(cls, datadict):
        '''Initialize Layer from a JSON blob

        la = Layer.fromjson(my_json)

        '''
        # return cls(datadict.items())
        pass

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
