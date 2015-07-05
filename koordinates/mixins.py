# -*- coding: utf-8 -*-

"""
koordinates.mixins
~~~~~~~~~~~~~~

This module provides mixin classes used in the Koordinates
Client Library

"""
import abc
import logging
import pprint
import json

import requests
import dateutil.parser
from six.moves import urllib

from .utils import (
    dump_class_attributes_to_dict,
    remove_empty_from_dict,
)
from .exceptions import (
    KoordinatesException,
    KoordinatesValueException,
    InvalidAPIVersion,
    InvalidURL,
    NotAuthorised,
    UnexpectedServerResponse,
    OnlyOneFilterAllowed,
    FilterMustNotBeSpaces,
    NotAValidBasisForFiltration,
    OnlyOneOrderingAllowed,
    NotAValidBasisForOrdering,
    AttributeNameIsReserved,
    ServerTimeOut,
    RateLimitExceeded,
    ImportEncounteredUpdateConflict,
    PublishAlreadyStarted,
    InvalidPublicationResourceList
)

logger = logging.getLogger(__name__)

class KoordinatesURLMixin(object):
    '''
    A Mixin to support URL operations
    '''
    URL_TEMPLATES = {
        'CONN': {
            'POST': {
                'publishmulti': '/publish/',
            },
        },
        'LAYER': {
            'GET': {
                'singleversion': '/layers/{layer_id}/versions/{version_id}/',
                'single': '/layers/{layer_id}/',
                'multi': '/layers/',
                'multidraft': '/layers/drafts/',
            },
            'POST': {
                'create': '/layers/',
                'update': '/layers/{layer_id}/import/',
            },
        },
        'SET': {
            'GET': {
                'single': '/sets/{set_id}/',
                'multi': '/sets/',
            },
        },
        'VERSION': {
            'GET': {
                'single': '/layers/{layer_id}/versions/{version_id}/',
                'multi': '/layers/{layer_id}/versions/',
            },
            'POST': {
                'import': '/layers/{layer_id}/versions/{version_id}/import/',
                'publish': '/layers/{layer_id}/versions/{version_id}/publish/',
            },
        },
        'DATA': {
            'GET': {
                'multi': '/data/',
                'single': '/data/{data_id}',
            },
        },
        'TABLE': {
            'GET': {
                'singleversion': '/tables/{table_id}/versions/{version_id}/',
            },
        },
        'PUBLISH': {
            'GET': {
                'single': '/publish/{publish_id}/',
                'multi': '/publish/',
            },
            'DELETE': {
                'single': '/publish/{publish_id}/',
            }
        },
        'TOKEN': {
            'GET': {
                'single': '/tokens/{token_id}/',
                'multi': '/tokens/',
            },
            'POST': {
                'create': '/tokens/',
            },
            'PUT': {
                'update': '/tokens/{token_id}/',
            },
            'DELETE': {
                'single': '/tokens/{token_id}/',
            },
        },
    }

    def get_url(self, datatype, verb, urltype, optargs=None ):
        """Returns a fully formed url

        :param datatype: a string identifying the data the url will access .
        :param verb: the HTTP verb needed for use with the url .
        :param urltype: an adjective used to the nature of the request .
        :param \*\*optargs: Optional arguments that allows override of the hostname or api version to be embedded in teh resulting url.
        :return: string
        :rtype: A fully formed url.
        """
        if optargs is None:
            optargs = {}

        if "hostname" not in optargs:
            try:
                optargs['hostname'] = self._parent.host
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Connection`
                # object itself
                optargs['hostname'] = self.host
        if "api_version" not in optargs:
            try:
                optargs['api_version'] = self._parent.api_version
            except AttributeError:
                # We need to cater for when `get_url` is
                # invoked from a method on the `Connection`
                # object itself
                optargs['api_version'] = self.api_version

        url = "https://{hostname}/services/api/{api_version}"
        url += self.URL_TEMPLATES[datatype][verb][urltype]
        return url.format(**optargs)




class KoordinatesObjectMixin(object):
    '''
    A Mixin providing the generic aspects of server interations
    for subclasses
    '''
    __metaclass__ = abc.ABCMeta

    def create(self, target_url):
        """Creates a object based on contents value of `id`.

        """

        json_headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        json_body = dump_class_attributes_to_dict(self)
        logger.debug('First pass JSON body for create follows')
        logger.debug(pprint.pformat(json_body))

        json_body = remove_empty_from_dict(json_body)
        logger.debug('Second pass JSON body for create follows')
        logger.debug(pprint.pformat(json_body))

        self._raw_response = requests.post(target_url,
                                           json=json_body,
                                           headers = self._parent.assemble_headers('POST', json_headers))

        if self._raw_response.status_code == 201:
            logger.debug('Return value from successful instance create follows')
            logger.debug(pprint.pformat(self._raw_response.text))

            good_layer_dict = self._raw_response.json()

            self.created_at = self.__make_date_if_possible(good_layer_dict['created_at'])
            self.created_by = good_layer_dict['created_by']
            self.url = good_layer_dict['url']
        elif self._raw_response.status_code == 401:
            raise NotAuthorised
        elif self._raw_response.status_code == 404:
            raise InvalidURL
        elif self._raw_response.status_code == 429:
            raise RateLimitExceeded
        elif self._raw_response.status_code == 504:
            raise ServerTimeOut
        else:
            raise UnexpectedServerResponse(self._raw_response.status_code, " ", self._raw_response.text)


    @abc.abstractmethod
    def get(self, id, target_url, dynamic_build = False):
        """Fetches a single object determined by the value of `id`.

        :param id: ID for the new object.
        :param target_url: the url on which to do the GET .
        :param dynamic_build: When True the instance hierarchy arising from the
                              JSON returned is automatically build. When False
                              control is handed back to the calling subclass to
                              build the instance hierarchy based on pre-defined
                              classes.

                              An example of `dynamic_build` being False is that
                              the `Layer` class will have the JSON arising from
                              GET returned to it and will then follow processing
                              defined in `Layer.get` to create an instance of
                              `Layer` from the JSON returned.

                              NB: In later versions this flag will be withdrawn
                              and all processing will be done as if `dynamic_build`
                              was False.
        """

        self._raw_response = requests.get(target_url,
                                          headers = self._parent.assemble_headers('GET'))

        if self._raw_response.status_code == 200:
            # convert JSON to dict
            dic_json = json.loads(self._raw_response.text)
            # itererte over resulting dict
            if dynamic_build:
                # Build an instance hierarchy based on an introspection of the
                # JSON returned.
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
                # Return a representation of the JSON returned to calling subclass
                # method and allow that method to build the resulting instance
                # hierarchy
                return dic_json
        elif self._raw_response.status_code == 401:
            raise NotAuthorised
        elif self._raw_response.status_code == 404:
            raise InvalidURL(target_url)
        elif self._raw_response.status_code == 429:
            raise RateLimitExceeded
        elif self._raw_response.status_code == 504:
            raise ServerTimeOut
        else:
            raise UnexpectedServerResponse

    def __specify_page(self, value):
        pass

    def filter(self, value):
        if self._filtering_applied:
            raise OnlyOneFilterAllowed

        # Eventually this check will be a good deal more sophisticated
        # so it's here in its current form to some degree as a placeholder
        if value.isspace():
            raise FilterMustNotBeSpaces()

        self.add_query_component("q", value)
        self._filtering_applied = True
        return self

    def order_by(self, sort_key):
        if self._ordering_applied:
            raise OnlyOneOrderingAllowed
        if sort_key not in self._attribute_sort_candidates:
            raise NotAValidBasisForOrdering(sort_key)

        self.add_query_component("sort", sort_key)
        self._ordering_applied = True
        return self

    def add_query_component(self, argname, argvalue):

        # parse original string url
        url_data = urllib.parse.urlsplit(self._url)

        # parse original query-string
        qs_data = urllib.parse.parse_qs(url_data.query)

        # manipulate the query-string
        qs_data[argname] = [argvalue]

        # get the url with modified query-string
        self._url = url_data._replace(query=urllib.parse.urlencode(qs_data, True)).geturl()

    def execute_get_list(self, dynamic_build = False):
        """Fetches zero, one or more objects .

        :param dynamic_build: When True the instance hierarchy arising from the
                              JSON returned is automatically build. When False
                              control is handed back to the calling subclass to
                              build the instance hierarchy based on pre-defined
                              classes.

                              An example of `dynamic_build` being False is that
                              the `Layer` class will have the JSON arising from
                              GET returned to it and will then follow processing
                              defined in `Layer.get` to create an instance of
                              `Layer` from the JSON returned.

                              NB: In later versions this flag will be withdrawn
                              and all processing will be done as if `dynamic_build`
                              was False.
        """
        self._list_of_response_dicts = []
        self._next_page_number = 1
        self.add_query_component("page", self._next_page_number)
        self.__execute_get_list_no_generator()
        for list_of_responses in self._list_of_response_dicts:
            for response in list_of_responses:
                if dynamic_build:
                    this_object = self.__class__(self._parent)
                    for key, value in response.items():
                        setattr(this_object, key, value)
                    yield this_object
                else:
                    yield response
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
                                          headers = self._parent.assemble_headers('GET'))

        if self._raw_response.status_code == 200:
            # If only row is returned the JSON corresponds to a single dict,
            # if more than one row is returned the JSON corresponds to a list
            # of dicts. To make life simpler in the case of a single dict we
            # coerce the single dict into a list
            if isinstance(self._raw_response.json(), dict):
                response_json = [self._raw_response.json()]
            else:
                response_json = self._raw_response.json()

            self._list_of_response_dicts.append(response_json)
            if 'page-next' in self._raw_response.links:
                self._link_to_next_in_list = self._raw_response.links['page-next']['url']
            else:
                self._link_to_next_in_list = None
        elif self._raw_response.status_code == 401:
            raise NotAuthorised
        elif self._raw_response.status_code == 404:
            raise InvalidURL
        elif self._raw_response.status_code == 429:
            raise RateLimitExceeded
        elif self._raw_response.status_code == 504:
            raise ServerTimeOut
        else:
            raise UnexpectedServerResponse

    def __create_attribute(self, att_name, att_value):
        if att_name in self._attribute_reserved_names:
            errmsg = """The name '{attname}' is not able to be used """ \
                     """an attribute name for the class '{classname}' """ \
                     """as it appears in the '_attribute_reserved_names' """ \
                     """list""".format(attname=att_name, classname=type(self).__name__)
            raise AttributeNameIsReserved(errmsg)

        if isinstance(att_value, list):
            att_value = [self.__make_date_if_possible(v) for v in att_value]
        else:
            att_value = self.__make_date_if_possible(att_value)

        setattr(self, att_name, att_value)

    def __make_date(self, value):
        '''
        `value` should either be a string
        parseable as a date/time; an empty
        string; or None

        Return either a `DateTime` corresponding
        to `value` or an empty String
        '''
        if value == "" or value is None:
            return ""
        else:
            return dateutil.parser.parse(value)


    def __make_date_if_possible(self, value):
        '''
        Try converting the value to a date
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


