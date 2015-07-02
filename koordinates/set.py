# -*- coding: utf-8 -*-

"""
koordinates.set
~~~~~~~~~~~~~~

This module provides the `Set` class used in the Koordinates
Client Library

"""

import logging

from .mixins import KoordinatesObjectMixin, KoordinatesURLMixin
from .layer import Group, Metadata
from .utils import make_list_of_Categories, make_date


logger = logging.getLogger(__name__)


class Set(KoordinatesObjectMixin, KoordinatesURLMixin):
    '''A Set

    TODO: Description of what a `Set` is

    '''
    def __init__(self,
                 parent=None,
                 id=None,
                 title=None,
                 description=None,
                 description_html=None,
                 categories=None,
                 tags=None,
                 group=None,
                 items=None,
                 url=None,
                 url_html=None,
                 metadata=None,
                 created_at=None):

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

        self._initialize_named_attributes(id,
                                          title,
                                          description,
                                          description_html,
                                          categories,
                                          tags,
                                          group,
                                          items,
                                          url,
                                          url_html,
                                          metadata,
                                          created_at)

        super(self.__class__, self).__init__()


    def _initialize_named_attributes(self,
                                     id,
                                     title,
                                     description,
                                     description_html,
                                     categories,
                                     tags,
                                     group,
                                     items,
                                     url,
                                     url_html,
                                     metadata,
                                     created_at):
        '''
        `_initialize_named_attributes` initializes those
        attributes of `Set` which are not prefixed by an
        underbar. Such attributes are named so as to indicate
        that they are, in terms of the API, "real" attributes
        of a `Set`. That is to say an attribute which is returned
        from the server when a given `Set` is requested. Other
        attributes, such as `_attribute_reserved_names` have leading
        underbar to indicate they are not derived from data returned
        from the server
        '''
        '''
        "id": 933,
        "title": "Ultra Fast Broadband Initiative Coverage",
        "description": "",
        "description_html": "",
        "categories": [],
        "tags": [],
        "group": {"id": 141, "url": "https://koordinates.com/services/api/v1/groups/141/", "name": "New Zealand Broadband Map", "country": "NZ"},
        "items": ["https://koordinates.com/services/api/v1/layers/4226/", "https://koordinates.com/services/api/v1/layers/4228/", "https://koordinates.com/services/api/v1/layers/4227/", "https://koordinates.com/services/api/v1/layers/4061/", "https://koordinates.com/services/api/v1/layers/4147/", "https://koordinates.com/services/api/v1/layers/4148/"],
        "url": "https://koordinates.com/services/api/v1/sets/933/",
        "url_html": "https://koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/",
        "metadata": null,
        "created_at": "2012-03-21T21:49:51.420Z"
        '''
        self.id = id
        self.title = title
        self.description = description
        self.description_html = description_html
        self.categories = categories if categories else []
        self.tags = tags if tags else []
        self.group = group if group else Group()
        self.items = items
        self.url = url
        self.url_html = url_html
        self.metadata = metadata if metadata else Metadata()
        self.created_at = created_at

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

        dic_set_as_json = super(self.__class__, self).get(id, target_url)

        self._initialize_named_attributes(id = dic_set_as_json.get("id"),
                                          title = dic_set_as_json.get("title"),
                                          description = dic_set_as_json.get("description"),
                                          description_html = dic_set_as_json.get("description_html"),
                                          categories = make_list_of_Categories(dic_set_as_json.get("categories")),
                                          tags = dic_set_as_json.get("tags"),
                                          group = Group.from_dict(dic_set_as_json.get("group")),
                                          items = dic_set_as_json.get("items", []),
                                          url = dic_set_as_json.get("url"),
                                          url_html = dic_set_as_json.get("url_html"),
                                          metadata = Metadata.from_dict(dic_set_as_json.get("metadata")),
                                          created_at = make_date(dic_set_as_json.get("created_at")))



