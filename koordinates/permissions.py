# -*- coding: utf-8 -*-

"""
koordinates.permissions
==================

For getting, editing and updating permissions via
the `Permissions API <https://help.koordinates.com/api/publisher-admin-api/permissions-api/>`_.

"""
import logging

from . import base
from . import exceptions
from .users import Group, User


logger = logging.getLogger(__name__)


class PermissionManager(base.InnerManager):
    """
    Accessor for querying and updating permissions.

    Access via the ``permissions`` property of :py:class:`koordinates.layers.Layer`
    or :py:class:`koordinates.sets.Set` instances.
    """

    _URL_KEY = 'PERMISSION'

    def __init__(self, client, parent_object):
        super(PermissionManager, self).__init__(client, parent_object._manager)
        self.parent_object = parent_object

    def create(self, permission):
        """
        Create single permission for the given object.

        :param Permission permission: A single Permission object to be set.
        """
        parent_url = self.client.get_url(self.parent_object._manager._URL_KEY, 'GET', 'single', {'id': self.parent_object.id})
        target_url = parent_url + self.client.get_url_path(self._URL_KEY, 'POST', 'single')
        r = self.client.request('POST', target_url, json=permission._serialize())
        return permission._deserialize(r.json(), self)

    def set(self, permissions):
        """
        Set the object permissions. If the parent object already has permissions, they will be overwritten.

        :param [] permissions: A group of Permission objects to be set.
        """
        parent_url = self.client.get_url(self.parent_object._manager._URL_KEY, 'GET', 'single', {'id': self.parent_object.id})
        target_url = parent_url + self.client.get_url_path(self._URL_KEY, 'PUT', 'multi')
        r = self.client.request('PUT', target_url, json=permissions)
        if r.status_code != 201:
            raise exceptions.ServerError("Expected 201 response, got %s: %s" % (r.status_code, target_url))
        return self.list()

    def list(self):
        """
        List permissions for the given object.
        """
        parent_url = self.client.get_url(self.parent_object._manager._URL_KEY, 'GET', 'single', {'id': self.parent_object.id})
        target_url = parent_url + self.client.get_url_path(self._URL_KEY, 'GET', 'multi')
        return base.Query(self, target_url)

    def get(self, permission_id, expand=[]):
        """
        List a specific permisison for the given object.

        :param str permission_id: the id of the Permission to be listed.
        """
        parent_url = self.client.get_url(self.parent_object._manager._URL_KEY, 'GET', 'single', {'id': self.parent_object.id})
        target_url = parent_url + self.client.get_url_path(
            self._URL_KEY, 'GET', 'single', {'permission_id': permission_id})
        return self._get(target_url, expand=expand)


class Permission(base.InnerModel):
    """
    Represents a permissions for a specific :py:class:`koordinates.layers.Layer`
    or :py:class:`koordinates.sets.Set` instance.
    """
    def _deserialize(self, data, manager):
        super(Permission, self)._deserialize(data, manager, manager.parent_object)
        self.group = Group()._deserialize(data['group'], manager.client.get_manager(Group)) if data.get('group') else None
        self.user = User()._deserialize(data['user'],  manager.client.get_manager(User)) if data.get('user') else None
        return self

    class Meta:
        manager = PermissionManager


class PermissionObjectMixin(object):
    """
    Mixin to be used in any Koordinates Object class that supports permissions. Also remember to set the Meta
    required fields:
    ```
        class Meta:
            serialize_skip = ('permissions',)
            deserialize_skip = ('permissions',)
    ```
    """

    _perms = None

    @property
    def permissions(self):
        if not self._perms:
            self._perms = PermissionManager(self._client, self)
        return self._perms
