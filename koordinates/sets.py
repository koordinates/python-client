# -*- coding: utf-8 -*-

"""
koordinates.sets
================

The `Sets API <https://help.koordinates.com/api/publisher-admin-api/sets-api/>`_
is used for grouping layers, tables and documents together.
"""

import logging

from koordinates.permissions import PermissionObjectMixin
from koordinates.users import Group
from koordinates.metadata import Metadata, MetadataManager
from koordinates import base
from koordinates.utils import is_bound


logger = logging.getLogger(__name__)


class SetManager(base.Manager):
    """
    Accessor for querying Sets.

    Access via the ``sets`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'SET'

    def __init__(self, client):
        super(SetManager, self).__init__(client)
        # Inner model managers
        self._metadata = MetadataManager(self, client)

    def create(self, set):
        """
        Creates a new Set.
        """
        target_url = self.client.get_url('SET', 'POST', 'create')
        r = self.client.request('POST', target_url, json=set._serialize())
        return set._deserialize(r.json(), self)

    def set_metadata(self, set_id, fp):
        """
        Set the XML metadata on a set.

        :param file fp: file-like object to read the XML metadata from.
        """
        base_url = self.client.get_url('SET', 'GET', 'single', {'id': set_id})
        self._metadata.set(base_url, fp)


class Set(base.Model, PermissionObjectMixin):
    '''
    Represents a single set grouping of layers, tables, and documents.
    '''
    class Meta:
        manager = SetManager
        serialize_skip = ('permissions',)
        deserialize_skip = ('permissions',)

    def _deserialize(self, data, manager):
        super(Set, self)._deserialize(data, manager)
        self.group = Group()._deserialize(data['group'], manager.client.get_manager(Group)) if data.get("group") else None
        self.metadata = Metadata()._deserialize(data["metadata"], manager._metadata, self) if data.get("metadata") else None
        return self

    @is_bound
    def save(self):
        """
        Saves changes to a Set.
        """
        target_url = self._client.get_url('SET', 'PUT', 'update', {'id': self.id})
        r = self._client.request('PUT', target_url, json=self._serialize())
        return self._deserialize(r.json(), self._manager)

    @is_bound
    def set_metadata(self, fp):
        """
        Set the XML metadata on a set.

        :param file fp: file-like object to read the XML metadata from.
        """
        base_url = self._client.get_url('SET', 'GET', 'single', {'id': self.id})
        self._manager._metadata.set(base_url, fp)

        # reload myself
        r = self._client.request('GET', base_url)
        return self._deserialize(r.json(), self._manager)
