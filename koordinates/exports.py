# -*- coding: utf-8 -*-

"""
koordinates.exports
===================

The `Exports API <https://support.koordinates.com/hc/en-us/articles/208580966>`_
provides an interface to create exports and download data from a Koordinates site.
"""
import logging

from . import base
from . import exceptions
from .utils import is_bound


logger = logging.getLogger(__name__)


class CropLayerManager(base.Manager):
    """
    Accessor for querying Crop Layers.

    Access via the ``exports.croplayers`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'CROPLAYER'

    def get_feature(self, croplayer_id, cropfeature_id):
        """
        Gets a crop feature

        :param int croplayer_id: ID of a cropping layer
        :param int cropfeature_id: ID of a cropping feature
        :rtype: CropFeature
        """
        target_url = self.client.get_url('CROPFEATURE', 'GET', 'single', {'croplayer_id': croplayer_id, 'cropfeature_id': cropfeature_id})
        return self.client.get_manager(CropFeature)._get(target_url)


class CropLayer(base.Model):
    """
    A crop layer provides features that can be used to crop exports to a geographic extent.
    """
    class Meta:
        manager = CropLayerManager
        relations = {
            'features': ['CropFeature'],
        }

    @is_bound
    def get_feature(self, cropfeature_id):
        """
        Gets a crop feature

        :param int cropfeature_id: ID of a cropping feature
        :rtype: CropFeature
        """
        return self._manager.get_feature(self.id, cropfeature_id)


class CropFeatureManager(base.Manager):
    """
    Accessor for querying Crop Features.
    """

    _URL_KEY = 'CROPFEATURE'


class CropFeature(base.Model):
    """
    A crop feature provides complex pre-defined geographic extents for cropping
    and clipping Exports.
    """
    class Meta:
        manager = CropFeatureManager
        relations = {
            'layer': CropLayer,
        }

    def _serialize(self):
        return self.url


class ExportManager(base.Manager):
    """
    Accessor for querying and creating Exports.

    Access via the ``exports`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'EXPORT'
    _options_cache = None

    @property
    def croplayers(self):
        """
        Returns a manager for querying and listing CropLayer models

        :rtype: CropLayerManager
        """
        return self.client.get_manager(CropLayer)

    def create(self, export):
        """
        Create and start processing a new Export.

        :param Export export: The Export to create.
        :rtype: Export
        """
        target_url = self.client.get_url(self._URL_KEY, 'POST', 'create')
        r = self.client.request('POST', target_url, json=export._serialize())
        return export._deserialize(r.json(), self)

    def validate(self, export):
        """
        Validates an Export.


        :param Export export:
        :rtype: ExportValidationResponse
        """
        target_url = self.client.get_url(self._URL_KEY, 'POST', 'validate')
        response_object = ExportValidationResponse()
        r = self.client.request('POST', target_url, json=export._serialize())
        return response_object._deserialize(r.json())

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

        .. code-block:: python

            {
                "vector": {
                    "application/x-ogc-gpkg": "GeoPackage",
                    "application/x-zipped-shp": "Shapefile",
                    #...
                },
                "table": {
                    "text/csv": "CSV (text/csv)",
                    "application/x-ogc-gpkg": "GeoPackage",
                    #...
                },
                "raster": {
                    "image/jpeg": "JPEG",
                    "image/jp2": "JPEG2000",
                    #...
                },
                "grid": {
                    "application/x-ogc-aaigrid": "ASCII Grid",
                    "image/tiff;subtype=geotiff": "GeoTIFF",
                    #...
                },
                "rat": {
                    "application/x-erdas-hfa": "ERDAS Imagine",
                    #...
                }
            }

        :rtype: dict
        """
        format_opts = self._options()['actions']['POST']['formats']['children']
        r = {}
        for kind, kind_opts in format_opts.items():
            r[kind] = {c['value']: c['display_name'] for c in kind_opts['choices']}
        return r


class ExportValidationResponse(base.SerializableBase):
    """
    Repsonse returned by Export validation requests.
    """

    def __init__(self, **kwargs):
        self.items = []
        super(ExportValidationResponse, self).__init__(**kwargs)

    def is_valid(self):
        """
        Test if the entire Export was valid

        :rtype: bool
        """
        for item in self.items:
            if not item['valid']:
                return False
        return True


class Export(base.Model):
    """
    An export is a request to extract data from a Koordinates site into an archive for downloading

    :Example:

    >>> export = koordinates.Export()
    >>> export.crs = "ESPG:4326"
    >>> export.formats = {
            "vector": "application/x-zipped-shp"
        }
    >>> export.add_item(layer)
    >>> client.exports.create(export)
    """
    class Meta:
        manager = ExportManager

    def __init__(self, **kwargs):
        self.items = []
        super(Export, self).__init__(**kwargs)

    def add_item(self, item, **options):
        """
        Add a layer or table item to the export.

        :param Layer|Table item: The Layer or Table to add
        :rtype: self
        """
        export_item = {
            "item": item.url,
        }
        export_item.update(options)
        self.items.append(export_item)
        return self

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
        :param int chunk_size: Chunk size in bytes for streaming large downloads. 10MB by default
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
