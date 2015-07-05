# -*- coding: utf-8 -*-

"""
koordinates.set
~~~~~~~~~~~~~~

This module provides the `Set` class used in the Koordinates
Client Library

"""

import logging

from .layer import Group, Metadata
from .utils import make_list_of_Categories
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
        self.categories = make_list_of_Categories(data.get("categories"))
        #self.group = Group().deserialize(data['group']) if data.get("group") else None
        self.items = data.get("items", [])
        #self.metadata = Metadata().deserialize(data['metadata']) if data.get("metadata") else None
        return self
