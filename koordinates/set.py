# -*- coding: utf-8 -*-

"""
koordinates.set
~~~~~~~~~~~~~~

This module provides the `Set` class used in the Koordinates
Client Library

"""

import logging

from .users import Group
from .metadata import Metadata
from . import base


logger = logging.getLogger(__name__)


class SetManager(base.Manager):
    URL_KEY = 'SET'


class Set(base.Model):
    '''A Set

    TODO: Description of what a `Set` is

    '''
    class Meta:
        manager = SetManager

    def deserialize(self, data, manager):
        super(Set, self).deserialize(data, manager)
        self.group = Group().deserialize(data['group'], manager.connection.get_manager(Group)) if data.get("group") else None
        self.metadata = Metadata().deserialize(data['metadata'], manager.connection.get_manager(Metadata)) if data.get("metadata") else None
        return self
