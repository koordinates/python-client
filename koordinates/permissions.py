# -*- coding: utf-8 -*-

"""
koordinates.permissions
==================

For getting, editing and updating permissions via
the `Permissions API <https://help.koordinates.com/api/publisher-admin-api/permissions-api/>`_.

"""
from koordinates.users import Group, User

import logging

from . import base


logger = logging.getLogger(__name__)


class BasePermissionManager(base.Manager):
    _URL_KEY = 'PERMISSION'
    _OBJECT_TYPE = None

    def create(self, object_id, permission):
        target_url = self.client.get_url(self._URL_KEY, 'POST', self._OBJECT_TYPE, {'%s_id' % self._OBJECT_TYPE: object_id})
        r = self.client.request('POST', target_url, json=permission._serialize())
        return permission._deserialize(r.json(), self)

    def list(self, object_id):
        target_url = self.client.get_url(
            self._URL_KEY, 'GET',
            self._OBJECT_TYPE,
            {'%s_id' % self._OBJECT_TYPE: object_id})
        return base.Query(self, target_url)

    def get(self, object_id, permission_id, expand=[]):
        target_url = self.client.get_url(
            self._URL_KEY, 'GET',
            '%s_single' % self._OBJECT_TYPE,
            {'%s_id' % self._OBJECT_TYPE: object_id, 'id': permission_id})
        return self._get(target_url, expand=expand)


class LayerPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'layer'


class SourcePermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'source'


class TablePermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'table'


class DocumentPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'document'


class SetPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'set'


class BasePermission(object):
    def _deserialize(self, data, manager):
        super(BasePermission, self)._deserialize(data, manager)
        self.group = Group()._deserialize(data['group'], manager.client.get_manager(Group)) if data.get("group") else None
        self.user = User()._deserialize(data["user"],  manager.client.get_manager(User)) if data.get("user") else None
        return self


class LayerPermission(BasePermission, base.Model):
    '''
    Represents a single Permission applied on a Layer.
    '''
    class Meta:
        manager = LayerPermissionManager


class SourcePermission(BasePermission, base.Model):
    '''
    Represents a single Permission applied on a Source.
    '''
    class Meta:
        manager = SourcePermissionManager


class TablePermission(BasePermission, base.Model):
    '''
    Represents a single Permission applied on a Table.
    '''
    class Meta:
        manager = TablePermissionManager


class DocumentPermission(BasePermission, base.Model):
    '''
    Represents a single Permission applied on a Document.
    '''
    class Meta:
        manager = DocumentPermissionManager


class SetPermission(BasePermission, base.Model):
    '''
    Represents a single Permission applied on a Set.
    '''
    class Meta:
        manager = SetPermissionManager
