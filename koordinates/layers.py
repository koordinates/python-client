# -*- coding: utf-8 -*-

"""
koordinates.layers
==================

For getting, editing and updating layers and tables.

"""
import logging

from .utils import (
    make_date,
    make_date_list_from_string_list,
)
from . import base
from .licenses import License
from .metadata import Metadata
from .publishing import Publish
from .users import Group
from .utils import is_bound


logger = logging.getLogger(__name__)


class LayerManager(base.Manager):
    URL_KEY = 'LAYER'

    def __init__(self, client):
        super(LayerManager, self).__init__(client)
        # Inner model managers
        self.versions = LayerVersionManager(client, self)
        self.data = LayerDataManager(client, self)

    def list_drafts(self):
        """
        Fetches a set of layers
        """
        target_url = self.client.get_url('LAYER', 'GET', 'multidraft')
        return base.Query(self, target_url)

    def create(self, layer):
        target_url = self.client.get_url('LAYER', 'POST', 'create')
        r = self.client.request('POST', target_url, json=layer.serialize())
        return layer.deserialize(r.json(), self)


class Layer(base.Model):
    '''A Layer

    Layers are objects on the map that consist of one or more separate items,
    but are manipulated as a single unit. Layers generally reflect collections
    of objects that you add on top of the map to designate a common
    association.
    '''
    class Meta:
        manager = LayerManager
        filter_attributes = (
            'kind', 'public', 'group', 'license', 'category',
            'geotag', 'tag', 'q', 'created_at', 'updated_at',
        )
        ordering_attributes = ('name', 'created_at', 'updated_at', 'popularity',)

    def deserialize(self, data, manager):
        super(Layer, self).deserialize(data, manager)
        self.group = Group().deserialize(data["group"], manager.client.get_manager(Group)) if data.get("group") else None
        self.data = LayerData().deserialize(data["data"], manager.data) if data.get("data") else None
        self.version = LayerVersion().deserialize(data["version"], manager.versions) if data.get("version") else None
        self.collected_at = [make_date(d) for d in data["collected_at"]] if data.get('collected_at') else None
        self.license = License().deserialize(data["license"], manager.client.get_manager(License)) if data.get("license") else None
        self.metadata = Metadata().deserialize(data["metadata"], manager.client.get_manager(Metadata)) if data.get("metadata") else None
        return self

    @is_bound
    def list_versions(self):
        target_url = self._client.get_url('VERSION', 'GET', 'multi', {'layer_id': self.id})
        return base.Query(self._manager, target_url)

    @is_bound
    def get_version(self, version_id, expand=[]):
        target_url = self._client.get_url('VERSION', 'GET', 'single', {'layer_id': self.id, 'version_id': version_id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def get_draft_version(self, expand=[]):
        target_url = self._client.get_url('VERSION', 'GET', 'draft', {'layer_id': self.id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def create_draft_version(self):
        target_url = self._client.get_url('VERSION', 'POST', 'create', {'layer_id': self.id})
        r = self._client.request('POST', target_url)
        return self._manager.create_from_result(r.json())

    @is_bound
    def get_published_version(self, expand=[]):
        target_url = self._client.get_url('VERSION', 'GET', 'published', {'layer_id': self.id})
        return self._manager._get(target_url, expand=expand)

    @is_bound
    def start_import(self, version_id=None):
        """ Starts importing this draft layerversion (cancelling any running import), even if the data object hasn’t changed from the previous version."""
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url('VERSION', 'POST', 'import', {'layer_id': self.id, 'version_id': version_id})
        r = self._client.request('POST', target_url)
        return self.deserialize(r.json(), self._manager)

    @is_bound
    def start_update(self):
        """
        A shortcut to create a new version and start importing it.
        Effectively the same as :py:meth:`create_draft_version`_ followed by :py:meth:`start_import`_.
        """
        target_url = self._client.get_url('LAYER', 'POST', 'update', {'layer_id': self.id})
        r = self._client.request('POST', target_url)
        return self._manager.create_from_result(r.json())

    @is_bound
    def publish(self, version_id=None):
        if not version_id:
            version_id = self.version.id

        target_url = self._client.get_url('VERSION', 'POST', 'publish', {'layer_id': self.id, 'version_id': version_id})
        r = self._client.request('POST', target_url)
        return self._client.get_manager(Publish).create_from_result(r.json())

    @is_bound
    def save(self):
        target_url = self._client.get_url('VERSION', 'PUT', 'edit', {'layer_id': self.id, 'version_id': self.version.id})
        r = self._manager.request('PUT', target_url, json=self.serialize())
        return self.deserialize(r.json(), self._manager)


class LayerVersionManager(base.InnerManager):
    URL_KEY = 'VERSION'

    def __init__(self, client, parent):
        super(LayerVersionManager, self).__init__(client)
        self._parent = parent

    def list(self, layer_id):
        target_url = self.client.get_url('VERSION', 'GET', 'multi', {'layer_id': layer_id})
        return base.Query(self._parent, target_url)

    def get(self, layer_id, version_id, expand=[]):
        target_url = self.client.get_url('VERSION', 'GET', 'single', {'layer_id': layer_id, 'version_id': version_id})
        return self._parent._get(target_url, expand=expand)

    def get_draft(self, layer_id, expand=[]):
        target_url = self.client.get_url('VERSION', 'GET', 'draft', {'layer_id': layer_id})
        return self._parent._get(target_url, expand=expand)

    def create_draft(self, layer_id):
        target_url = self.client.get_url('VERSION', 'POST', 'create', {'layer_id': layer_id})
        r = self.client.request('POST', target_url)
        return self._parent.create_from_result(r.json())

    def get_published(self, layer_id, expand=[]):
        target_url = self.client.get_url('VERSION', 'GET', 'published', {'layer_id': layer_id})
        return self._parent._get(target_url, expand=expand)

    def start_import(self, layer_id, version_id):
        """ Starts importing this draft layerversion (cancelling any running import), even if the data object hasn’t changed from the previous version."""
        target_url = self.client.get_url('VERSION', 'POST', 'import', {'layer_id': layer_id, 'version_id': version_id})
        r = self.client.request('POST', target_url)
        return self._parent.create_from_result(r.json())

    def start_update(self, layer_id):
        """
        A shortcut to create a new version and start importing it.
        Effectively the same as :py:meth:`create_draft_version`_ followed by :py:meth:`start_import`_.
        """
        target_url = self.client.get_url('LAYER', 'POST', 'update', {'layer_id': layer_id})
        r = self.client.request('POST', target_url)
        return self._parent.create_from_result(r.json())


class LayerVersion(base.Model):
    class Meta:
        manager = LayerVersionManager



class LayerDataManager(base.InnerManager):
    URL_KEY = 'DATA'

    def __init__(self, client, parent):
        super(LayerDataManager, self).__init__(client)
        self._parent = parent


class LayerData(base.Model):
    class Meta:
        manager = LayerDataManager


# Aliases
Table = Layer
TableManager = LayerManager
