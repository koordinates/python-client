# -*- coding: utf-8 -*-

"""
koordinates.sets
================

For grouping layers, tables and documents together.

"""

import logging

from .users import Group
from .metadata import Metadata, MetadataManager
from . import base
from .utils import is_bound


logger = logging.getLogger(__name__)


class SetManager(base.Manager):
    URL_KEY = 'SET'

    def __init__(self, client):
        super(SetManager, self).__init__(client)
        # Inner model managers
        self.metadata = MetadataManager(self)


    def create(self, set):
        target_url = self.client.get_url('SET', 'POST', 'create')
        r = self.client.request('POST', target_url, json=set.serialize())
        return set.deserialize(r.json(), self)

class Set(base.Model):
    ''' For grouping layers, tables and documents together. '''
    class Meta:
        manager = SetManager

    def __getattr__(self, name):     
        print('attr: ', name)
        return 1

    def deserialize(self, data, manager):
        super(Set, self).deserialize(data, manager)
        self.group = Group().deserialize(data['group'], manager.client.get_manager(Group)) if data.get("group") else None
        self.metadata = Metadata().deserialize(data['metadata'], manager.client.get_manager(Metadata)) if data.get("metadata") else Metadata()
        return self

    @is_bound
    def save(self):
        target_url = self._client.get_url('SET', 'PUT', 'update', {'set_id': self.id})
        r = self._client.request('PUT', target_url, json=self.serialize())
        return self.deserialize(r.json(), self._manager)



