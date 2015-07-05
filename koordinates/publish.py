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
from .users import User


logger = logging.getLogger(__name__)

class PublishManager(base.Manager):
    URL_KEY = 'PUBLISH'


class Publish(base.Model):
    """
    The Group Publishing API allows for draft versions of versioned objects
    (Documents, Layers and Tables) to be scheduled for publishing together.

    A Publish object describes an active publishing group.
    """
    class Meta:
        manager = PublishManager
        attribute_filter_candidates = ('state', 'reference',)

    def cancel(self):
        """ Cancel a pending publish task """
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


