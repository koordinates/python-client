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
from .publishing import Publish

logger = logging.getLogger(__name__)


class SetManager(base.Manager):
    """
    Accessor for querying Sets.

    Access via the ``sets`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = "SET"

    def __init__(self, client):
        super(SetManager, self).__init__(client)
        # Inner model managers
        self.versions = SetVersionManager(client, self)
        self._data = SetDataManager(client, self)
        self._metadata = MetadataManager(self, client)

    def list_drafts(self):
        """
        A filterable list view of sets, returning the draft version of each set.
        If the most recent version has been published already, it won’t be returned here.
        """
        target_url = self.client.get_url("SET", "GET", "multidraft")
        return base.Query(self, target_url)

    def create(self, set):
        """
        Creates a new Set.
        """
        target_url = self.client.get_url("SET", "POST", "create")
        r = self.client.request("POST", target_url, json=set._serialize())
        return set._deserialize(r.json(), self)

    def list_versions(self, set_id):
        """
        Filterable list of versions of a set, always ordered newest to oldest.

        If the version’s source supports revisions, you can get a specific revision using
        ``.filter(data__source_revision=value)``. Specific values depend on the source type.
        Use ``data__source_revision__lt`` or ``data__source_revision__gte`` to filter
        using ``<`` or ``>=`` operators respectively.
        """
        target_url = self.client.get_url("SET_VERSION", "GET", "multi", {"id": set_id})
        return base.Query(
            self,
            target_url,
            valid_filter_attributes=("data",),
            valid_sort_attributes=(),
        )

    def get_version(self, set_id, version_id, expand=[]):
        """
        Get a specific version of a set.
        """
        target_url = self.client.get_url(
            "SET_VERSION", "GET", "single", {"id": set_id, "version_id": version_id},
        )
        return self._get(target_url, expand=expand)

    def get_draft(self, set_id, expand=[]):
        """
        Get the current draft version of a set.
        :raises NotFound: if there is no draft version.
        """
        target_url = self.client.get_url("SET_VERSION", "GET", "draft", {"id": set_id})
        return self._get(target_url, expand=expand)

    def get_published(self, set_id, expand=[]):
        """
        Get the latest published version of this set.
        :raises NotFound: if there is no published version.
        """
        target_url = self.client.get_url(
            "SET_VERSION", "GET", "published", {"id": set_id}
        )
        return self._get(target_url, expand=expand)

    def create_draft(self, set_id):
        """
        Creates a new draft version.

        :rtype: Client
        :return: the new version
        :raises 409 Conflict: if there is already a draft version for this set.
        """
        target_url = self.client.get_url(
            "SET_VERSION", "POST", "create", {"id": set_id}
        )
        r = self.client.request("POST", target_url, json={})
        return self.create_from_result(r.json())

    def set_metadata(self, set_id, fp):
        """
        Set the XML metadata on a set.

        :param file fp: file-like object to read the XML metadata from.
        """
        base_url = self.client.get_url("SET", "GET", "single", {"id": set_id})
        self._metadata.set(base_url, fp)


class Set(base.Model, PermissionObjectMixin):
    """
    Represents a single set grouping of layers, tables, and documents.
    """

    class Meta:
        manager = SetManager
        serialize_skip = ("permissions",)
        deserialize_skip = ("permissions",)

    def _deserialize(self, data, manager):
        super(Set, self)._deserialize(data, manager)
        self.group = (
            Group()._deserialize(data["group"], manager.client.get_manager(Group))
            if data.get("group")
            else None
        )
        self.metadata = (
            Metadata()._deserialize(data["metadata"], manager._metadata, self)
            if data.get("metadata")
            else None
        )
        self.version = (
            SetVersion()._deserialize(data["version"], manager.versions, self)
            if data.get("version")
            else None
        )
        return self

    @is_bound
    def set_metadata(self, fp, version_id=None):
        """
        Set the XML metadata on this draft version.

        :param file fp: file-like object to read the XML metadata from.
        :raises NotAllowed: if this version is already published.
        """
        if not version_id:
            version_id = self.version.id

        base_url = self._client.get_url(
            "SET_VERSION", "GET", "single", {"id": self.id, "version_id": version_id},
        )
        self._manager._metadata.set(base_url, fp)

        # reload myself
        r = self._client.request("GET", base_url)
        return self._deserialize(r.json(), self._manager)

    @property
    def is_published_version(self):
        """ Return if this version is the published version of a layer """
        pub_ver = getattr(self, "published_version", None)
        this_ver = getattr(self, "this_version", None)
        return this_ver and pub_ver and (this_ver == pub_ver)

    @property
    def is_draft_version(self):
        """ Return if this version is the draft version of a layer """
        pub_ver = getattr(self, "published_version", None)
        latest_ver = getattr(self, "latest_version", None)
        this_ver = getattr(self, "this_version", None)
        return (
            this_ver
            and latest_ver
            and (this_ver == latest_ver)
            and (latest_ver != pub_ver)
        )

    @is_bound
    def list_versions(self):
        """
        Filterable list of versions of a set, always ordered newest to oldest.

        If the version’s source supports revisions, you can get a specific revision using
        ``.filter(data__source_revision=value)``. Specific values depend on the source type.
        Use ``data__source_revision__lt`` or ``data__source_revision__gte`` to filter
        using ``<`` or ``>=`` operators respectively.
        """
        target_url = self._client.get_url(
            "SET_VERSION", "GET", "multi", {"id": self.id}
        )
        return base.Query(
            self._manager,
            target_url,
            valid_filter_attributes=("data",),
            valid_sort_attributes=(),
        )

    @is_bound
    def get_version(self, version_id, expand=()):
        """
        Get a specific version of this set
        """
        target_url = self._client.get_url(
            "SET_VERSION", "GET", "single", {"id": self.id, "version_id": version_id},
        )
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def get_draft_version(self, expand=()):
        """
        Get the current draft version of this set.
        :raises NotFound: if there is no draft version.
        """
        target_url = self._client.get_url(
            "SET_VERSION", "GET", "draft", {"id": self.id}
        )
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def get_published_version(self, expand=()):
        """
        Get the latest published version of this set.
        :raises NotFound: if there is no published version.
        """
        target_url = self._client.get_url(
            "SET_VERSION", "GET", "published", {"id": self.id}
        )
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def publish(self, version_id=None):
        """
        Creates a publish task for this version.

        :return: the publish task
        :rtype: Publish
        :raises Conflict: If the version is already published, or already has a publish job.
        """
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url(
            "SET_VERSION", "POST", "publish", {"id": self.id, "version_id": version_id},
        )
        r = self._client.request("POST", target_url, json={})
        return self._client.get_manager(Publish).create_from_result(r.json())

    @is_bound
    def save(self):
        """
        Edits this draft version.

        :raises NotAllowed: if the version is already published.
        """
        target_url = self._client.get_url(
            "SET_VERSION",
            "PUT",
            "edit",
            {"id": self.id, "version_id": self.version.id},
        )
        r = self._client.request("PUT", target_url, json=self._serialize())
        return self._deserialize(r.json(), self._manager)

    @is_bound
    def delete_version(self, version_id=None):
        """
        Deletes this draft version (revert to published)

        :raises NotAllowed: if this version is already published.
        :raises Conflict: if this version is already deleted.
        """
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url(
            "SET_VERSION",
            "DELETE",
            "single",
            {"id": self.id, "version_id": version_id},
        )
        self._client.request("DELETE", target_url)


class SetVersionManager(base.InnerManager):
    _URL_KEY = "SET_VERSION"


class SetVersion(base.InnerModel):
    """
    Represents the ``version`` property of a :py:class:`koordinates.client.Client` instance.
    """

    class Meta:
        manager = SetVersionManager


class SetDataManager(base.InnerManager):
    _URL_KEY = "DATA"


class SetData(base.InnerModel):
    """
    Represents the ``data`` property of a :py:class:`koordinates.client.Client` instance.
    """

    class Meta:
        manager = SetDataManager
