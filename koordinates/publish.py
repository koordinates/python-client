# -*- coding: utf-8 -*-

"""
koordinates.publish
~~~~~~~~~~~~~~

This module provides the `Publish` and associated classes used in
the Koordinates Client Library

"""

import logging

from . import base

from .utils import make_list_of_Categories, make_date

from .utils import (
    remove_empty_from_dict,
    dump_class_attributes_to_dict,
    make_date_list_from_string_list,
    make_date,
    make_date_if_possible,
    make_list_of_Datasources,
    make_list_of_Fields,
    make_list_of_Categories
)
from koordinates.layer import Createdby


logger = logging.getLogger(__name__)

class PublishManager(base.Manager):
    def list(self, *args, **kwargs):
        """Fetches a set of sets
        """
        target_url = self.connection.get_url('PUBLISH', 'GET', 'multi')
        return super(PublishManager, self).list(target_url)

    def get(self, id, **kwargs):
        """Fetches a Publish determined by the value of `id`.

        :param id: ID for the new :class:`Publish`  object.
        """
        target_url = self.connection.get_url('PUBLISH', 'GET', 'single', {'publish_id': id})
        return super(PublishManager, self).get(target_url, id, **kwargs)


class Publish(base.Model):
    '''A Publish

    TODO: Description of what a `Publish` is

    '''
    '''
    "id": 2054,
    "url": "https://test.koordinates.com/services/api/v1/publish/2054/",
    "state": "completed",
    "created_at": "2015-06-08T03:40:40.368Z",
    "created_by": {"id": 18504, "url": "https://test.koordinates.com/services/api/v1/users/18504/", "first_name": "Richard", "last_name": "Shea", "country": "NZ"},
    "error_strategy": "abort",
    "publish_strategy": "together",
    "publish_at": null,
    "items": ["https://test.koordinates.com/services/api/v1/layers/8092/versions/9822/"]
    '''
    class Meta:
        manager = PublishManager
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
        `_initialize_named_attributes` initializes those
        attributes of `Publish` which are not prefixed by an
        underbar. Such attributes are named so as to indicate
        that they are, in terms of the API, "real" attributes
        of a `Publish`. That is to say an attribute which is returned
        from the server when a given `Publish` is requested. Other
        attributes, such as `_attribute_reserved_names` have leading
        underbar to indicate they are not derived from data returned
        from the server

        '''

        self.id = data.get("id")
        self.url = data.get("url")
        self.state = data.get("state")
        self.created_at = make_date(data.get("created_at"))
        self.created_by = Createdby.from_dict(data.get("created_by")) if data.get("created_by") else Createdby()
        self.error_strategy = data.get("error_strategy")
        self.publish_strategy = data.get("publish_strategy")
        self.publish_at = make_date(data.get("publish_at"))
        self.items = data.get("items") if data.get("items") else []



    def cancel(self):
        """Cancel a pending publish task
        """
        assert type(self.id) is int,\
            "The 'id' attribute is not an integer, it should be - have you fetched a publish record ?"

        target_url = self.get_url('PUBLISH', 'DELETE', 'single', {'publish_id': self.id})
        json_headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        self._raw_response = requests.delete(target_url,
                                           headers=json_headers,
                                           auth=self._parent.get_auth())

        if self._raw_response.status_code == 202:
            # Success !
            pass
        elif self._raw_response.status_code == 409:
            # Indicates that the publish couldn't be cancelled as the
            # Publish process has already started
            raise PublishAlreadyStarted
        else:
            raise UnexpectedServerResponse


