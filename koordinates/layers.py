# -*- coding: utf-8 -*-

"""
koordinates.layers
==================

For getting, editing and updating layers and tables, via
the `Layers & Tables API <https://help.koordinates.com/api/publisher-admin-api/layers-tables-api/>`_.

"""
import logging

from .utils import make_date
from . import base
from .licenses import License
from .metadata import Metadata, MetadataManager
from .permissions import PermissionObjectMixin
from .publishing import Publish
from .users import Group
from .utils import is_bound


logger = logging.getLogger(__name__)


class LayerManager(base.Manager):
    """
    Accessor for querying Layers & Tables.

    Access via the ``layers`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'LAYER'

    def __init__(self, client):
        super(LayerManager, self).__init__(client)
        # Inner model managers
        self.versions = LayerVersionManager(client, self)
        self._data = LayerDataManager(client, self)
        self._metadata = MetadataManager(client, self)

    def list_drafts(self):
        """
        A filterable list views of layers, returning the draft version of each layer.
        If the most recent version of a layer or table has been published already,
        it won’t be returned here.
        """
        target_url = self.client.get_url('LAYER', 'GET', 'multidraft')
        return base.Query(self, target_url)

    def create(self, layer):
        """
        Creates a new layer.
        All attributes except ``name`` and ``data.datasources`` are optional.
        :return: the new draft version of the layer.
        """
        target_url = self.client.get_url('LAYER', 'POST', 'create')
        r = self.client.request('POST', target_url, json=layer._serialize())
        return layer._deserialize(r.json(), self)

    def list_versions(self, layer_id):
        """
        Filterable list of versions of a layer, always ordered newest to oldest.

        If the version’s source supports revisions, you can get a specific revision using
        ``.filter(data__source__revision=value)``. Specific values depend on the source type.
        Use ``data__source_revision__lt`` or ``data__source_revision__gte`` to filter
        using ``<`` or ``>=`` operators respectively.
        """
        target_url = self.client.get_url('VERSION', 'GET', 'multi', {'layer_id': layer_id})
        return base.Query(self, target_url, valid_filter_attributes=('data',), valid_sort_attributes=())

    def get_version(self, layer_id, version_id, expand=[]):
        """
        Get a specific version of a layer.
        """
        target_url = self.client.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id})
        return self._get(target_url, expand=expand)

    def get_draft(self, layer_id, expand=[]):
        """
        Get the current draft version of a layer.
        :raises NotFound: if there is no draft version.
        """
        target_url = self.client.get_url('VERSION', 'GET', 'draft', {'layer_id': layer_id})
        return self._get(target_url, expand=expand)

    def get_published(self, layer_id, expand=[]):
        """
        Get the latest published version of this layer.
        :raises NotFound: if there is no published version.
        """
        target_url = self.client.get_url('VERSION', 'GET', 'published', {'layer_id': layer_id})
        return self._get(target_url, expand=expand)

    def create_draft(self, layer_id):
        """
        Creates a new draft version.

        If anything in the data object has changed then an import will begin immediately.
        Otherwise to force a re-import from the previous sources call :py:meth:`koordinates.layers.LayerManager.start_import`.

        :rtype: Layer
        :return: the new version
        :raises Conflict: if there is already a draft version for this layer.
        """
        target_url = self.client.get_url('VERSION', 'POST', 'create', {'layer_id': layer_id})
        r = self.client.request('POST', target_url, json={})
        return self.create_from_result(r.json())

    def start_import(self, layer_id, version_id):
        """
        Starts importing the specified draft version (cancelling any running import),
        even if the data object hasn’t changed from the previous version.
        """
        target_url = self.client.get_url('VERSION', 'POST', 'import', {'layer_id': layer_id, 'version_id': version_id})
        r = self.client.request('POST', target_url, json={})
        return self.create_from_result(r.json())

    def start_update(self, layer_id):
        """
        A shortcut to create a new version and start importing it.
        Effectively the same as :py:meth:`koordinates.layers.LayerManager.create_draft` followed by :py:meth:`koordinates.layers.LayerManager.start_import`.
        """
        target_url = self.client.get_url('LAYER', 'POST', 'update', {'layer_id': layer_id})
        r = self.client.request('POST', target_url, json={})
        return self.parent.create_from_result(r.json())

    def set_metadata(self, layer_id, version_id, fp):
        """
        Set the XML metadata on a layer draft version.

        :param file fp: file-like object to read the XML metadata from.
        :raises NotAllowed: if the version is already published.
        """
        base_url = self.client.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id})
        self._metadata.set(base_url, fp)


class Layer(base.Model, PermissionObjectMixin):
    '''
    Represents a version of a single Layer or Table.
    '''

    class Meta:
        manager = LayerManager
        filter_attributes = (
            'kind', 'public', 'group', 'license', 'category',
            'geotag', 'tag', 'q', 'created_at', 'updated_at',
        )
        ordering_attributes = ('name', 'created_at', 'updated_at', 'popularity',)
        serialize_skip = ('permissions',)
        deserialize_skip = ('permissions',)

    def _serialize(self, with_data=True):
        o = super(Layer, self)._serialize()
        if not with_data and ('data' in o):
            del o['data']
        return o

    def _deserialize(self, data, manager):
        super(Layer, self)._deserialize(data, manager)
        self.group = Group()._deserialize(data["group"], manager.client.get_manager(Group)) if data.get("group") else None
        self.data = LayerData()._deserialize(data["data"], manager._data, self) if data.get("data") else None
        self.version = LayerVersion()._deserialize(data["version"], manager.versions, self) if data.get("version") else None
        self.collected_at = [make_date(d) for d in data["collected_at"]] if data.get('collected_at') else None
        self.license = License()._deserialize(data["license"], manager.client.get_manager(License)) if data.get("license") else None
        self.metadata = Metadata()._deserialize(data["metadata"], manager._metadata, self) if data.get("metadata") else None
        return self

    @property
    def is_published_version(self):
        """ Return if this version is the published version of a layer """
        pub_ver = getattr(self, 'published_version', None)
        this_ver = getattr(self, 'this_version', None)
        return this_ver and pub_ver and (this_ver == pub_ver)

    @property
    def is_draft_version(self):
        """ Return if this version is the draft version of a layer """
        pub_ver = getattr(self, 'published_version', None)
        latest_ver = getattr(self, 'latest_version', None)
        this_ver = getattr(self, 'this_version', None)
        return this_ver and latest_ver and (this_ver == latest_ver) and (latest_ver != pub_ver)

    @is_bound
    def list_versions(self):
        """
        Filterable list of versions of a layer, always ordered newest to oldest.

        If the version’s source supports revisions, you can get a specific revision using
        ``.filter(data__source__revision=value)``. Specific values depend on the source type.
        Use ``data__source_revision__lt`` or ``data__source_revision__gte`` to filter
        using ``<`` or ``>=`` operators respectively.
        """
        target_url = self._client.get_url('VERSION', 'GET', 'multi', {'layer_id': self.id})
        return base.Query(self._manager, target_url, valid_filter_attributes=('data',), valid_sort_attributes=())

    @is_bound
    def get_version(self, version_id, expand=[]):
        """
        Get a specific version of this layer
        """
        target_url = self._client.get_url('VERSION', 'GET', 'single', {'layer_id': self.id, 'version_id': version_id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def get_draft_version(self, expand=[]):
        """
        Get the current draft version of this layer.
        :raises NotFound: if there is no draft version.
        """
        target_url = self._client.get_url('VERSION', 'GET', 'draft', {'layer_id': self.id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def get_published_version(self, expand=[]):
        """
        Get the latest published version of this layer.
        :raises NotFound: if there is no published version.
        """
        target_url = self._client.get_url('VERSION', 'GET', 'published', {'layer_id': self.id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def create_draft_version(self):
        """
        Creates a new draft version from this model content.

        If anything in the data object has changed then an import will begin immediately.
        Otherwise to force a re-import from the previous sources call :py:meth:`koordinates.layers.Layer.start_import`.

        :rtype: Layer
        :return: the new version
        :raises Conflict: if there is already a draft version for this layer.
        """
        target_url = self._client.get_url('VERSION', 'POST', 'create', {'layer_id': self.id})
        r = self._client.request('POST', target_url, json={})
        return self._manager.create_from_result(r.json())

    @is_bound
    def start_import(self, version_id=None):
        """
        Starts importing this draft layerversion (cancelling any running import), even
        if the data object hasn’t changed from the previous version.

        :raises Conflict: if this version is already published.
        """
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url('VERSION', 'POST', 'import', {'layer_id': self.id, 'version_id': version_id})
        r = self._client.request('POST', target_url, json={})
        return self._deserialize(r.json(), self._manager)

    @is_bound
    def start_update(self):
        """
        A shortcut to create a new version and start importing it.
        Effectively the same as :py:meth:`.create_draft_version` followed by :py:meth:`koordinates.layers.Layer.start_import`.

        :rtype: Layer
        :return: the new version
        :raises Conflict: if there is already a draft version for this layer.
        """
        target_url = self._client.get_url('LAYER', 'POST', 'update', {'layer_id': self.id})
        r = self._client.request('POST', target_url, json={})
        return self._manager.create_from_result(r.json())

    @is_bound
    def publish(self, version_id=None):
        """
        Creates a publish task just for this version, which publishes as soon as any import is complete.

        :return: the publish task
        :rtype: Publish
        :raises Conflict: If the version is already published, or already has a publish job.
        """
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url('VERSION', 'POST', 'publish', {'layer_id': self.id, 'version_id': version_id})
        r = self._client.request('POST', target_url, json={})
        return self._client.get_manager(Publish).create_from_result(r.json())

    @is_bound
    def save(self, with_data=False):
        """
        Edits this draft layerversion.
        # If anything in the data object has changed, cancel any existing import and start a new one.

        :param bool with_data: if ``True``, send the data object, which will start a new import and cancel
            any existing one. If ``False``, the data object will *not* be sent, and no import will start.
        :raises NotAllowed: if the version is already published.
        """
        target_url = self._client.get_url('VERSION', 'PUT', 'edit', {'layer_id': self.id, 'version_id': self.version.id})
        r = self._client.request('PUT', target_url, json=self._serialize(with_data=with_data))
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

        target_url = self._client.get_url('VERSION', 'DELETE', 'single', {'layer_id': self.id, 'version_id': version_id})
        r = self._client.request('DELETE', target_url)
        logger.info("delete_version(): %s", r.status_code)

    @is_bound
    def delete_layer(self):
        """
        Delete this layer.
        """
        target_url = self._client.get_url('LAYER', 'DELETE', 'single', {'id': self.id})
        r = self._client.request('DELETE', target_url)
        logger.info("delete(): %s", r.status_code)

    @is_bound
    def set_metadata(self, fp, version_id=None):
        """
        Set the XML metadata on this draft version.

        :param file fp: file-like object to read the XML metadata from.
        :raises NotAllowed: if this version is already published.
        """
        if not version_id:
            version_id = self.version.id

        base_url = self._client.get_url('VERSION', 'GET', 'single', {'layer_id': self.id, 'version_id': version_id})
        self._manager._metadata.set(base_url, fp)

        # reload myself
        r = self._client.request('GET', base_url)
        return self._deserialize(r.json(), self._manager)


class LayerVersionManager(base.InnerManager):
    _URL_KEY = 'VERSION'


class LayerVersion(base.InnerModel):
    """
    Represents the ``version`` property of a :py:class:`.Layer` instance.
    """
    class Meta:
        manager = LayerVersionManager


class LayerDataManager(base.InnerManager):
    _URL_KEY = 'DATA'


class LayerData(base.InnerModel):
    """
    Represents the ``data`` property of a :py:class:`.Layer` instance.
    """
    class Meta:
        manager = LayerDataManager


# Aliases
Table = Layer
TableManager = LayerManager
