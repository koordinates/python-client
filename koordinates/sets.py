# -*- coding: utf-8 -*-

"""
koordinates.sets
================

For grouping layers, tables and documents together.

"""

import logging

from .users import Group
from .metadata import Metadata
from . import base


logger = logging.getLogger(__name__)


class SetManager(base.Manager):
    URL_KEY = 'SET'


class Set(base.Model):
    ''' For grouping layers, tables and documents together. '''
    class Meta:
        manager = SetManager

    def deserialize(self, data, manager):
        super(Set, self).deserialize(data, manager)
        self.group = Group().deserialize(data['group'], manager.client.get_manager(Group)) if data.get("group") else None
        self.metadata = Metadata().deserialize(data['metadata'], manager.client.get_manager(Metadata)) if data.get("metadata") else None
        return self
