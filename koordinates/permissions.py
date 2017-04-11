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

    def create(self, object_id, object_type, permission):
        target_url = self.client.get_url(self._URL_KEY, 'POST', object_type, {'%s_id' % object_type: object_id})
        r = self.client.request('POST', target_url, json=permission._serialize())
        return permission._deserialize(r.json(), self)

    def list(self, object_id, object_type):
        target_url = self.client.get_url(self._URL_KEY, 'GET', object_type, {'%s_id' % object_type: object_id})
        return base.Query(self, target_url)

    def get(self, object_id, object_type, permission_id, expand=[]):
        target_url = self.client.get_url(
            self._URL_KEY, 'GET',
            '%s_single' % object_type,
            {'%s_id' % object_type: object_id, 'id': permission_id})
        return self._get(target_url, expand=expand)


class LayerPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'layer'

    def create(self, layer_id, permission):
        """
        Creates a new Layer Permission.
        """
        return super(LayerPermissionManager, self).create(layer_id, self._OBJECT_TYPE, permission)

    def list(self, layer_id):
        """
        List a Layer Permissions.
        """
        return super(LayerPermissionManager, self).list(layer_id, self._OBJECT_TYPE)

    def get(self, layer_id, id, expand=[]):
        """
        Get a specific Permission
        """
        return super(LayerPermissionManager, self).get(layer_id, self._OBJECT_TYPE, id, expand)


class SourcePermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'source'

    def create(self, source_id, permission):
        """
        Creates a new Source Permission.
        """
        return super(SourcePermissionManager, self).create(source_id, self._OBJECT_TYPE, permission)

    def list(self, source_id):
        """
        List a Source Permissions.
        """
        return super(SourcePermissionManager, self).list(source_id, self._OBJECT_TYPE)


class TablePermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'table'

    def create(self, table_id, permission):
        """
        Creates a new Table Permission.
        """
        return super(TablePermissionManager, self).create(table_id, self._OBJECT_TYPE, permission)

    def list(self, table_id):
        """
        List a Table Permissions.
        """
        return super(TablePermissionManager, self).list(table_id, self._OBJECT_TYPE)


class DocumentPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'document'

    def create(self, document_id, permission):
        """
        Creates a new Document Permission.
        """
        return super(DocumentPermissionManager, self).create(document_id, self._OBJECT_TYPE, permission)

    def list(self, document_id):
        """
        List a Layer Permissions.
        """
        return super(DocumentPermissionManager, self).list(document_id, self._OBJECT_TYPE)


class SetPermissionManager(BasePermissionManager):
    _OBJECT_TYPE = 'set'

    def create(self, set_id, permission):
        """
        Creates a new Set Permission.
        """
        return super(SetPermissionManager, self).create(set_id, self._OBJECT_TYPE, permission)

    def list(self, set_id):
        """
        List a Layer Permissions.
        """
        return super(SetPermissionManager, self).list(set_id, self._OBJECT_TYPE)


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
