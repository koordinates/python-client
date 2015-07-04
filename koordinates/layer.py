# -*- coding: utf-8 -*-

"""
koordinates.layer
~~~~~~~~~~~~~~

This module provides the Layer, Version and classes on which they are
dependent upon within the Koordinates Client Library

"""
import logging

import six
import requests


from .mixins import KoordinatesObjectMixin, KoordinatesURLMixin

from .utils import (
    make_date,
    make_list_of_Datasources,
    make_list_of_Fields,
    make_list_of_Categories,
    make_date_list_from_string_list,
)
from . import base


logger = logging.getLogger(__name__)
class Version(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Version
    TODO: Explanation of what a `Version` is from Koordinates
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
                 publish_to_catalog_services=None,
                 permissions=None,
                 autoupdate=None,
                 supplier_reference=None,
                 elevation_field=None,
                 version_instance=None):

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


        self._initialize_named_attributes(id,
                                         url,
                                         type,
                                         name,
                                         first_published_at,
                                         published_at,
                                         description,
                                         description_html,
                                         group,
                                         data,
                                         url_html,
                                         published_version,
                                         latest_version,
                                         this_version,
                                         kind,
                                         categories,
                                         tags,
                                         collected_at,
                                         created_at,
                                         license,
                                         metadata,
                                         publish_to_catalog_services,
                                         permissions,
                                         autoupdate,
                                         supplier_reference,
                                         elevation_field,
                                         version_instance)

        super(self.__class__, self).__init__()

    def _initialize_named_attributes(self,
                                     id,
                                     url,
                                     type,
                                     name,
                                     first_published_at,
                                     published_at,
                                     description,
                                     description_html,
                                     group,
                                     data,
                                     url_html,
                                     published_version,
                                     latest_version,
                                     this_version,
                                     kind,
                                     categories,
                                     tags,
                                     collected_at,
                                     created_at,
                                     license,
                                     metadata,
                                     publish_to_catalog_services,
                                     permissions,
                                     autoupdate,
                                     supplier_reference,
                                     elevation_field,
                                     version_instance):
        '''
        `_initialize_named_attributes` initializes those
        attributes of `Version` which are not prefixed by an
        underbar. Such attributes are named so as to indicate
        that they are, in terms of the API, "real" attributes
        of a `Version`. That is to say an attribute which is returned
        from the server when a given `Version` is requested. Other
        attributes, such as `_attribute_reserved_names` have leading
        underbar to indicate they are not derived from data returned
        from the server

        '''

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
        self.publish_to_catalog_services = publish_to_catalog_services
        self.permissions = permissions
        self.autoupdate = autoupdate if autoupdate else Autoupdate()
        self.supplier_reference = supplier_reference
        self.elevation_field = elevation_field
        self.version_instance = version_instance if version_instance else Versioninstance()

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

        target_url = self.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id})
        dic_version_as_json = super(self.__class__, self).get(-1, target_url)

        self._initialize_named_attributes(id = dic_version_as_json.get("id"),
                                          url = dic_version_as_json.get("url"),
                                          type = dic_version_as_json.get("type"),
                                          name = dic_version_as_json.get("name"),
                                          first_published_at = make_date(dic_version_as_json.get("first_published_at")),
                                          published_at = make_date(dic_version_as_json.get("published_at")),
                                          description = dic_version_as_json.get("description"),
                                          description_html = dic_version_as_json.get("description_html"),
                                          group = Group.from_dict(dic_version_as_json.get("group")),
                                          data = Data.from_dict(dic_version_as_json.get("data")),
                                          url_html = dic_version_as_json.get("url_html"),
                                          published_version = dic_version_as_json.get("published_version"),
                                          latest_version = dic_version_as_json.get("latest_version"),
                                          this_version = dic_version_as_json.get("this_version"),
                                          kind = dic_version_as_json.get("kind"),
                                          categories = make_list_of_Categories(dic_version_as_json.get("categories")),
                                          tags = dic_version_as_json.get("tags"),
                                          collected_at = make_date_list_from_string_list(dic_version_as_json.get("collected_at", [])),
                                          created_at = make_date(dic_version_as_json.get("created_at")),
                                          license = License.from_dict(dic_version_as_json.get("license")),
                                          metadata = Metadata.from_dict(dic_version_as_json.get("metadata")),
                                          publish_to_catalog_services = dic_version_as_json.get("publish_to_catalog_services"),
                                          permissions = dic_version_as_json.get("permissions"),
                                          autoupdate = dic_version_as_json.get("autoupdate"),
                                          supplier_reference = dic_version_as_json.get("supplier_reference"),
                                          elevation_field = dic_version_as_json.get("elevation_field"),
                                          version_instance = Versioninstance.from_dict(dic_version_as_json.get("version")))

    def publish(self):
        """Publish the current Version
        """
        assert type(self.id) is int,\
            "The 'id' attribute is not an integer, it should be - have you fetched a version ?"
        assert type(self.version_instance.id) is int,\
            "The 'version_instance.id' attribute is not an integer, it should be - have you fetched a version ?"

        target_url = self.get_url('VERSION', 'POST', 'publish', {'layer_id': self.id, 'version_id': self.version_instance.id})
        json_headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        self._raw_response = requests.post(target_url,
                                           headers=self._parent.assemble_headers(json_headers))

        if self._raw_response.status_code == 201:
            # Success !
            pass
        elif self._raw_response.status_code == 404:
            # The resource specificed in the URL could not be found
            raise InvalidURL
        elif self._raw_response.status_code == 409:
            # Indicates that the request could not be processed because
            # of conflict in the request, such as an edit conflict in
            # the case of multiple updates
            raise ImportEncounteredUpdateConflict
        else:
            raise UnexpectedServerResponse

    def import_version(self, layer_id, version_id):
        """Reimport an existing layer from its previous datasources
        and create a new version
        """
        target_url = self.get_url('VERSION', 'POST', 'import', {'layer_id': layer_id, 'version_id': version_id})
        r = self._parent.request('POST', target_url)
        if r.status_code == 202:
            # Success ! Update accepted for Processing but not
            # necesarily complete
            pass
        elif r.status_code == 404:
            # The resource specificed in the URL could not be found
            raise InvalidURL
        elif r.status_code == 409:
            # Indicates that the request could not be processed because
            # of conflict in the request, such as an edit conflict in
            # the case of multiple updates
            raise ImportEncounteredUpdateConflict
        else:
            raise UnexpectedServerResponse


class Group(object):
    '''A Group
    TODO: Explanation of what a `Group` is from Koordinates

    NB: Currently this Class is only used as a component of `Layer`
    '''
    def __init__(self, id=None, url=None, name=None, country=None):
        self.id = id
        self.url = url
        self.name = name
        self.country = country

    @classmethod
    def from_dict(cls, dict_group):
        '''Initialize Group from a dict.

        la = Group.from_dict(a_dict)


        '''
        if dict_group:
            the_group = cls(dict_group.get("id", None),
                            dict_group.get("url", None),
                            dict_group.get("name", None),
                            dict_group.get("country", None))
        else:
            the_group = cls()

        return the_group


class Data(object):
    '''A Data
    TODO: Explanation of what a `Data` is from Koordinates

    NB: Currently `Data` is only used as a component of `Layer`
    '''
    def __init__(self, encoding=None, crs=None,
                 primary_key_fields=[],
                 datasources=[],
                 geometry_field=None,
                 fields=[]):

        assert type(primary_key_fields) is list,\
            "The 'Data' attribute 'primary_key_fields' must be a list"
        #assert type(datasources) is list,\
        #    "The 'Data' attribute 'datasources' must be a list"
        assert type(fields) is list,\
            "The 'Data' attribute 'fields' must be a list"
        #assert all(isinstance(ds_instance, Datasource) for ds_instance in datasources),\
        #    "The 'Data' attribute 'datasources' must be a list of Datasource objects"
        assert all(isinstance(f_instance, Field) for f_instance in fields),\
            "The 'Data' attribute 'fields' must be a list of Datasource objects"

        self.encoding = encoding
        self.crs = crs
        self.primary_key_fields = primary_key_fields
        self.datasources = datasources
        self.geometry_field = geometry_field
        self.fields = fields

    @classmethod
    def from_dict(cls, dict_data):
        '''Initialize Data from a dict.

        la = Data.from_dict(a_dict)


        '''
        if dict_data:
            # To allow for resuse across the API we allow for the
            # possibility that `datasources` is either : a string
            # (containing a url referencing a `datasources` object
            # or list of dictionaries defining one or more `datasources`
            # objects
            if isinstance(dict_data.get("datasources"), six.string_types):
                the_datasources = dict_data.get("datasources")
            else:
                the_datasources = make_list_of_Datasources(dict_data.get("datasources"))

            # Now build the `Data` object
            the_data = cls(dict_data.get("encoding"),
                           dict_data.get("crs"),
                           dict_data.get("primary_key_fields", []),
                           the_datasources,
                           dict_data.get("geometry_field"),
                           make_list_of_Fields(dict_data.get("fields")))
        else:
            the_data = cls()

        return the_data

class Datasource(object):
    '''A Datasource
    TODO: Explanation of what a `Datasource` is from Koordinates

    NB: Currently `Datasource` is only used as a component of `Layer`
    '''
    def __init__(self, id):
        self.id = id


class Category(object):
    '''A Category
    TODO: Explanation of what a `Category` is from Koordinates

    NB: Currently `Category` is only used as a component of `Layer`
    '''
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug

    @classmethod
    def from_dict(cls, dict_category):
        '''Initialize Category from a dict.
        '''
        if dict_category:
            the_category = cls(dict_category.get("name"),
                                 dict_category.get("slug"))
        else:
            the_category = cls()

        return the_category


class Autoupdate(object):
    '''A Autoupdate
    TODO: Explanation of what a `Autoupdate` is from Koordinates

    NB: Currently `Autoupdate` is only used as a component of `Version`
    '''
    def __init__(self, behaviour=None, schedule=None):
        self.behaviourk = behaviour
        self.schedule = schedule

    @classmethod
    def from_dict(cls, dict_autoupdate):
        '''Initialize License from a dict.

        la = License.from_dict(a_dict)


        '''
        if dict_autoupdate:
            the_autoupdate = cls(dict_autoupdate.get("behaviour"),
                                 dict_autoupdate.get("schedule"))
        else:
            the_autoupdate = cls()

        return the_autoupdate

class Createdby(object):
    '''A Createdby
    A basket of information identifying the creator
    '''
    def __init__(self,
                 id=None,
                 url=None,
                 first_name=None,
                 last_name=None,
                 country=None):

        self.id = id
        self.url = url
        self.first_name = first_name
        self.last_name = last_name
        self.country = country

    @classmethod
    def from_dict(cls, dict_createdby):
        '''Initialize Createdby from a dict.
        '''
        if dict_createdby:
            the_createdby = cls(dict_createdby.get("id"),
                              dict_createdby.get("url"),
                              dict_createdby.get("first_name"),
                              dict_createdby.get("last_name"),
                              dict_createdby.get("country"))
        else:
            the_createdby = cls()

        return the_createdby

class License(object):
    '''A License
    TODO: Explanation of what a `License` is from Koordinates

    NB: Currently `License` is only used as a component of `Layer`
    '''
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

    @classmethod
    def from_dict(cls, dict_license):
        '''Initialize License from a dict.

        la = License.from_dict(a_dict)


        '''
        if dict_license:
            the_license = cls(dict_license.get("id"),
                              dict_license.get("title"),
                              dict_license.get("type"),
                              dict_license.get("jurisdiction"),
                              dict_license.get("version"),
                              dict_license.get("url"),
                              dict_license.get("url_html"))
        else:
            the_license = cls()

        return the_license

class Versioninstance(object):
    '''A Versioninstance
    TODO: Explanation of what a `Versioninstance` is from Koordinates

    TODO: Rename this class `Versioninstance` is a very bad name for a
    class but I really wanted to push on when I encountered the need for the
    class.

    NB: Currently `Versioninstance` is only used as a component of `Version`
    '''
    def __init__(self,
                 id=None,
                 url=None,
                 status=None,
                 created_at=None,
                 created_by=None,
                 reference=None,
                 progress=None):

        self.id=id
        self.url=url
        self.status=status
        self.created_at=make_date(created_at)
        self.created_by=created_by
        self.reference=reference
        self.progress=progress

    @classmethod
    def from_dict(cls, dict_version_instance):
        '''Initialize License from a dict.

        la = License.from_dict(a_dict)


        '''
        if dict_version_instance:
            the_version_instance = cls(dict_version_instance.get("id"),
                              dict_version_instance.get("title"),
                              dict_version_instance.get("type"),
                              dict_version_instance.get("jurisdiction"),
                              dict_version_instance.get("version"),
                              dict_version_instance.get("url"),
                              dict_version_instance.get("url_html"))
        else:
            the_version_instance = cls()

        return the_version_instance

class Metadata(object):
    '''A Metadata
    TODO: Explanation of what a `Metadata` is from Koordinates

    NB: Currently `Metadata` is only used as a component of `Layer`
    '''
    def __init__(self, iso=None, dc=None, native=None):
        self.iso = iso
        self.dc = dc
        self.native = native

    @classmethod
    def from_dict(cls, dict_mdata):
        '''Initialize Metadata from a dict.

        la = Metadata.from_dict(a_dict)


        '''
        if dict_mdata:
            the_metadata = cls(dict_mdata.get("iso"),
                            dict_mdata.get("dc"),
                            dict_mdata.get("native"))
        else:
            the_metadata = cls()

        return the_metadata

class Field(object):
    '''A Field
    TODO: Explanation of what a `Field` is from Koordinates

    NB: Currently `Field` is only used as a component of `Layer`
    '''
    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type


class LayerManager(base.Manager):
    def list(self, *args, **kwargs):
        """Fetches a set of layers
        """
        target_url = self.connection.get_url('LAYER', 'GET', 'multi')
        return super(LayerManager, self).list(target_url)

    def list_drafts(self):
        """Fetches a set of layers
        """
        target_url = self.connection.get_url('LAYER', 'GET', 'multidraft')
        return super(LayerManager, self).list(target_url)

    def get(self, id, **kwargs):
        """Fetches a Layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer`  object.
        """
        target_url = self.connection.get_url('LAYER', 'GET', 'single', {'layer_id': id})
        return super(LayerManager, self).get(target_url, id, **kwargs)

class Layer(base.Model):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items,
    but are manipulated as a single unit. Layers generally reflect collections
    of objects that you add on top of the map to designate a common
    association.
    '''
    class Meta:
        manager = LayerManager
        attribute_sort_candidates = ('name',)
        attribute_filter_candidates = ('name',)

    def __init__(self, **kwargs):
        self._url = None
        self._id = kwargs.get('id', None)

        self.deserialize(kwargs)

        super(self.__class__, self).__init__()

#   def __init__(self,
#                parent=None,
#                id=None,
#                url=None,
#                type=None,
#                name=None,
#                first_published_at=None,
#                published_at=None,
#                description=None,
#                description_html=None,
#                group=None,
#                data=None,
#                url_html=None,
#                published_version=None,
#                latest_version=None,
#                this_version=None,
#                kind=None,
#                categories=None,
#                tags=None,
#                collected_at=None,
#                created_at=None,
#                license=None,
#                metadata=None,
#                elevation_field=None):

#       self._parent = parent
#       self._url = None
#       self._id = id
#       self._ordering_applied = False
#       self._filtering_applied = False

#       self._raw_response = None
#       self._list_of_response_dicts = []
#       self._link_to_next_in_list = ""
#       self._next_page_number = 1

#       self._attribute_sort_candidates = ['name']
#       self._attribute_filter_candidates = ['name']

#       # An attribute may not be created automatically
#       # due to JSON returned from the server with any
#       # names which appear in the list
#       # _attribute_reserved_names
#       self._attribute_reserved_names = ['version']

#       self._initialize_named_attributes(id,
#                                        url,
#                                        type,
#                                        name,
#                                        first_published_at,
#                                        published_at,
#                                        description,
#                                        description_html,
#                                        group,
#                                        data,
#                                        url_html,
#                                        published_version,
#                                        latest_version,
#                                        this_version,
#                                        kind,
#                                        categories,
#                                        tags,
#                                        collected_at,
#                                        created_at,
#                                        license,
#                                        metadata,
#                                        elevation_field)

#       super(self.__class__, self).__init__()

#   def _initialize_named_attributes(self,
#                                    id,
#                                    url,
#                                    type,
#                                    name,
#                                    first_published_at,
#                                    published_at,
#                                    description,
#                                    description_html,
#                                    group,
#                                    data,
#                                    url_html,
#                                    published_version,
#                                    latest_version,
#                                    this_version,
#                                    kind,
#                                    categories,
#                                    tags,
#                                    collected_at,
#                                    created_at,
#                                    license,
#                                    metadata,
#                                    elevation_field):
#       '''
#       `_initialize_named_attributes` initializes those
#       attributes of `Layer` which are not prefixed by an
#       underbar. Such attributes are named so as to indicate
#       that they are, in terms of the API, "real" attributes
#       of a `Layer`. That is to say an attribute which is returned
#       from the server when a given `Layer` is requested. Other
#       attributes, such as `_attribute_reserved_names` have leading
#       underbar to indicate they are not derived from data returned
#       from the server

#       '''

#       self.id = id
#       self.url = url
#       self.type = type
#       self.name = name
#       self.first_published_at = first_published_at
#       self.published_at = published_at
#       self.description = description
#       self.description_html = description_html
#       self.group = group if group else Group()
#       self.data = data if data else Data()
#       self.url_html = url_html
#       self.published_version = published_version
#       self.latest_version = latest_version
#       self.this_version = this_version
#       self.kind = kind
#       self.categories = categories if categories else []
#       self.tags = tags if tags else []
#       self.collected_at = collected_at
#       self.created_at = created_at
#       self.license = license if license else License()
#       self.metadata = metadata if metadata else Metadata()
#       self.elevation_field = elevation_field

    def deserialize(self, data):
        '''
        `deserialize` initializes those
        attributes of `Layer` which are not prefixed by an
        underbar. Such attributes are named so as to indicate
        that they are, in terms of the API, "real" attributes
        of a `Layer`. That is to say an attribute which is returned
        from the server when a given `Layer` is requested. Other
        attributes, such as `_attribute_reserved_names` have leading
        underbar to indicate they are not derived from data returned
        from the server

        '''

        self.id = data.get("id")
        self.url = data.get("url")
        self.type = data.get("type")
        self.name = data.get("name")
        self.first_published_at = make_date(data.get("first_published_at"))
        self.published_at = data.get("published_at")
        self.description = data.get("description")
        self.description_html = data.get("description_html")
        self.group = Group.from_dict(data.get("group")) if data.get("group") else Group()
        self.data = Data.from_dict(data.get("data")) if data.get("data") else Data()
        self.url_html = data.get("url_html")
        self.published_version = data.get("published_version")
        self.latest_version = data.get("latest_version")
        self.this_version = data.get("this_version")
        self.kind = data.get("kind")
        self.categories = make_list_of_Categories(data.get("categories"))
        self.tags = data.get("tags") if data.get("tags") else []
        self.collected_at = [make_date(str_date) for str_date in data.get("collected_at", [])]
        self.created_at = data.get("created_at")
        self.license = License.from_dict(data.get("license")) if data.get("license") else License()
        self.metadata = Metadata.from_dict(data.get("metadata")) if data.get("metadata") else Metadata()
        self.elevation_field = data.get("elevation_field")


    @classmethod
    def from_dict(cls, dict_layer):
        '''Initialize Layer from a dict.
        '''
        if dict_layer:
            the_layer = cls(None,
                            dict_layer.get("id", None),
                            dict_layer.get("url", None),
                            dict_layer.get("type", None),
                            dict_layer.get("name", None),
                            make_date(dict_layer.get("first_published_at", None)),
                            make_date(dict_layer.get("published_at", None)),
                            dict_layer.get("description", None),
                            dict_layer.get("description_html", None),
                            Group.from_dict(dict_layer.get("group", None)),
                            Data.from_dict(dict_layer.get("data", None)),
                            dict_layer.get("url_html", None),
                            dict_layer.get("published_version", None),
                            dict_layer.get("latest_version", None),
                            dict_layer.get("this_version", None),
                            dict_layer.get("kind", None),
                            make_list_of_Categories(dict_layer.get("categories", None)),
                            dict_layer.get("tags", None),
                            [make_date(str_date) for str_date in dict_layer.get("collected_at", [])],
                            make_date(dict_layer.get("created_at", None)),
                            License.from_dict(dict_layer.get("license", None)),
                            Metadata.from_dict(dict_layer.get("metadata", None)),
                            dict_layer.get("elevation_field", None))
        else:
            the_layer = cls()

        return the_layer


    def get_list(self):
        """Fetches a set of layers
        """
        target_url = self.get_url('LAYER', 'GET', 'multi')
        self._url = target_url
        return self

#   def get_list_of_drafts(self):
#       """Fetches a set of layers
#       """
#       target_url = self.get_url('LAYER', 'GET', 'multidraft')
#       self._url = target_url
#       return self

    def execute_get_list(self):
        """Fetches zero, one or more Layers .

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
        for dic_layer_as_json in super(self.__class__, self).execute_get_list():
            the_layer =  Layer.from_dict(dic_layer_as_json)
            yield the_layer

    def get(self, id, dynamic_build = False):
        """Fetches a layer determined by the value of `id`.

        :param id: ID for the new :class:`Layer` object.
        """

        target_url = self.get_url('LAYER', 'GET', 'single', {'layer_id': id})
        # Call the superclass `get` with dynamic_build set to False
        dic_layer_as_json = super(self.__class__, self).get(id,
                                                            target_url,
                                                            dynamic_build)
        # Clear all existing attributes
        self._initialize_named_attributes(id = dic_layer_as_json.get("id"),
                                          url = dic_layer_as_json.get("url"),
                                          type = dic_layer_as_json.get("type"),
                                          name = dic_layer_as_json.get("name"),
                                          first_published_at = make_date(dic_layer_as_json.get("first_published_at")),
                                          published_at = make_date(dic_layer_as_json.get("published_at")),
                                          description = dic_layer_as_json.get("description"),
                                          description_html = dic_layer_as_json.get("description_html"),
                                          group = Group.from_dict(dic_layer_as_json.get("group")),
                                          data = Data.from_dict(dic_layer_as_json.get("data")),
                                          url_html = dic_layer_as_json.get("url_html"),
                                          published_version = dic_layer_as_json.get("published_version"),
                                          latest_version = dic_layer_as_json.get("latest_version"),
                                          this_version = dic_layer_as_json.get("this_version"),
                                          kind = dic_layer_as_json.get("kind"),
                                          categories = make_list_of_Categories(dic_layer_as_json.get("categories")),
                                          tags = dic_layer_as_json.get("tags"),
                                          collected_at = make_date_list_from_string_list(dic_layer_as_json.get("collected_at", [])),
                                          created_at = make_date(dic_layer_as_json.get("created_at")),
                                          license = License.from_dict(dic_layer_as_json.get("license")),
                                          metadata = Metadata.from_dict(dic_layer_as_json.get("metadata")),
                                          elevation_field = dic_layer_as_json.get("elevation_field"))


    def create(self):
        """Creates a layer based on the current attributes of the
        `Layer` instance.

        """
        target_url = self.get_url('LAYER', 'POST', 'create')
        super(self.__class__, self).create(target_url)

    def update(self):
        target_url = self.get_url('LAYER', 'POST', 'import')
        self._parent.request()
