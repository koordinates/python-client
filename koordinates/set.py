# -*- coding: utf-8 -*-

"""
koordinates.set
~~~~~~~~~~~~~~

This module provides the `Set` class used in the Koordinates
Client Library

"""

import logging

from .layer import Group, Metadata
from .utils import make_list_of_Categories, make_date
from koordinates.base import BaseManager, BaseModel, Query


logger = logging.getLogger(__name__)



class SetManager(BaseManager):
    def list(self, *args, **kwargs):
        """Fetches a set of sets
        """
        target_url = self.connection.get_url('SET', 'GET', 'multi')
        return Query(self.model, target_url)

    def get(self, id):
        """Fetches a Set determined by the value of `id`.

        :param id: ID for the new :class:`Set`  object.
        """

        target_url = self.connection.get_url('SET', 'GET', 'single', {'set_id': id})
        r = self.connection.request('GET', target_url)
        r.raise_for_status()
        return self.create_from_result(r.json())


class Set(BaseModel):
    '''A Set

    TODO: Description of what a `Set` is

    '''
    class Meta:
        manager = SetManager
        attribute_sort_candidates = ('name',)
        attribute_filter_candidates = ('name',)
        #attribute_reserved_names = []

    def __init__(self, **kwargs):
        self._url = None
        self._id = kwargs.get('id', None)

        self.deserialize(kwargs)

        super(self.__class__, self).__init__()

    def deserialize(self, data):
        '''
        `deserialize` initializes those
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
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.description_html = data.get("description_html")
        self.categories = make_list_of_Categories(data.get("categories"))
        self.tags = data.get("tags")
        self.group = Group.from_dict(data.get("group"))
        self.items = data.get("items", [])
        self.url = data.get("url")
        self.url_html = data.get("url_html")
        self.metadata = Metadata.from_dict(data.get("metadata"))
        self.created_at = make_date(data.get("created_at"))

        # An attribute may not be created automatically
        # due to JSON returned from the server with any
        # names which appear in the list
        # _attribute_reserved_names


