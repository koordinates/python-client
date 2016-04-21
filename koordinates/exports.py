# -*- coding: utf-8 -*-

"""
koordinates.exports
==================

TODO: Add description

"""
import logging

from . import base
from . import exceptions
from .utils import is_bound


logger = logging.getLogger(__name__)


class CropLayerManager(base.Manager):
    """
    TODO: Docs
    """

    _URL_KEY = 'CROPLAYER'

    def get_feature(self, croplayer_id, cropfeature_id):
        """
        TODO: Docs
        """
        target_url = self.client.get_url('CROPFEATURE', 'GET', 'single', {'croplayer_id': croplayer_id, 'cropfeature_id': cropfeature_id})
        return self.client.get_manager(CropFeature)._get(target_url)


class CropLayer(base.Model):
    """
    TODO: Docs
    """
    class Meta:
        manager = CropLayerManager
        relations = {
            'features': ['CropFeature'],
        }

    @is_bound
    def get_feature(self, cropfeature_id):
        """
        TODO: Docs
        """
        return self._manager.get_feature(self.id, cropfeature_id)


class CropFeatureManager(base.Manager):
    """
    TODO: Docs
    """

    _URL_KEY = 'CROPFEATURE'


class CropFeature(base.Model):
    """
    TODO: Docs
    """
    class Meta:
        manager = CropFeatureManager
        relations = {
            'layer': CropLayer,
        }


class ExportManager(base.Manager):
    """
    TODO: Docs
    """

    _URL_KEY = 'EXPORT'
    _options_cache = None

    def create(self, export):
        """
        Creates a new Export.
        """
        target_url = self.client.get_url(self._URL_KEY, 'POST', 'create')
        r = self.client.request('POST', target_url, json=export._serialize())
        return export._deserialize(r.json(), self)

    def validate(self, export):
        """
        Validates an Export.
        """
        target_url = self.client.get_url(self._URL_KEY, 'POST', 'validate')
        r = self.client.request('POST', target_url, json=export._serialize())
        return export._deserialize(r.json(), self)

    def _options(self):
        """
        Returns a raw options object
        :rtype: dict
        """
        if self._options_cache is None:
            target_url = self.client.get_url(self._URL_KEY, 'OPTIONS', 'options')
            r = self.client.request('OPTIONS', target_url)
            self._options_cache = r.json()
        return self._options_cache

    def get_formats(self):
        """
        Returns a dictionary of format options keyed by data kind.
        """
        return self._options()['actions']['POST']['formats']['children']


class Export(base.Model):
    """
    TODO: Docs
    """
    class Meta:
        manager = ExportManager

    def __init__(self, **kwargs):
        self.items = []
        super(Export, self).__init__(**kwargs)

    def _deserialize(self, data, manager):
        super(Export, self)._deserialize(data, manager)
        return self

    def add_item(self, layer=None, table=None, **options):
        """
        TODO Docs
        """
        item = layer or table
        assert item

        export_item = {
            "item": item.url,
        }
        export_item.update(options)
        self.items.append(export_item)

    @is_bound
    def cancel(self):
        """
        Cancel the export processing
        """
        r = self._client.request('DELETE', self.url)

    @is_bound
    def download(self, filename=None, chunk_size=10*1024**2, download_progress_callback=None):
        """
        Download the export archive.

        :param str filename: Path and filename to download the export to. If unset, defaults to 
                the the export's name in the current working directory.
        :param int chunk_size: Chunk size for streaming large downloads. 10MB by default
        :param function download_progress_callback: An optional callback
                    function which receives upload progress notifications. The function should take two
                    arguments: the number of bytes recieved, and the total number of bytes to recieve.
        :rtype: str
        """
        filename = filename or "{}.zip".format(self.name)
        progress_size = 0

        r = self._manager.client.request('GET', self.download_url, stream=True)
        total_content_length = r.headers.get('content-length', None)

        with open(filename, 'wb') as file_handle:
            for chunk in r.iter_content(chunk_size=chunk_size):
                file_handle.write(chunk)
                progress_size += len(chunk)
                if download_progress_callback:
                    download_progress_callback(progress_size, total_content_length)

        return filename
