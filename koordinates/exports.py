# -*- coding: utf-8 -*-

"""
koordinates.exports
===================

The `Exports API <https://support.koordinates.com/hc/en-us/articles/208580966>`_
provides an interface to create exports and download data from a Koordinates site.
"""
import collections
import logging
import os
import six

if six.PY2:
    import contextlib2 as contextlib
else:
    import contextlib

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

    def cancel(self, export_id):
        target_url = self.client.get_url(self._URL_KEY, 'DELETE', 'single', {'id': export_id})
        r = self.client.request('DELETE', target_url)
        return self.create_from_result(r.json())

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

    def get_reasons(self):
        r = {}
        if self.invalid_reasons:
            r['__all__'] = self.invalid_reasons[:]
        for item in self.items:
            if item['invalid_reasons']:
                r[item['item']] = item['invalid_reasons'][:]
        return r


class DownloadError(exceptions.ClientError):
    pass


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

    def set_formats(self, **kinds):
        if not hasattr(self, 'formats'):
            self.formats = {}

        for kind, data_format in kinds.items():
            if data_format:
                self.formats[kind] = data_format
            elif kind in self.formats:
                del self.formats[kind]

        return self.formats

    @is_bound
    def cancel(self):
        """
        Cancel the export processing
        """
        return self._manage.cancel(self.id)

    @is_bound
    def download(self, path, progress_callback=None, chunk_size=1024**2):
        """
        Download the export archive.

        .. warning::

            If you pass this function an open file-like object as the ``path``
            parameter, the function will not close that file for you.

        If a ``path`` parameter is a directory, this function will use the
        Export name to determine the name of the file (returned). If the
        calculated download file path already exists, this function will raise
        a DownloadError.

        You can also specify the filename as a string. This will be passed to
        the built-in :func:`open` and we will read the content into the file.

        Instead, if you want to manage the file object yourself, you need to
        provide either a :class:`io.BytesIO` object or a file opened with the
        `'b'` flag. See the two examples below for more details.

        :param path: Either a string with the path to the location
            to save the response content, or a file-like object expecting bytes.
        :param function progress_callback: An optional callback
                function which receives upload progress notifications. The function should take two
                arguments: the number of bytes recieved, and the total number of bytes to recieve.
        :param int chunk_size: Chunk size in bytes for streaming large downloads and progress reporting. 1MB by default
        :returns The name of the automatic filename that would be used.
        :rtype: str
        """
        if not self.download_url or self.state != 'complete':
            raise DownloadError("Download not available")

        # ignore parsing the Content-Disposition header, since we know the name
        download_filename = "{}.zip".format(self.name)
        fd = None

        if isinstance(getattr(path, 'write', None), collections.Callable):
            # already open file-like object
            fd = path
        elif os.path.isdir(path):
            # directory to download to, using the export name
            path = os.path.join(path, download_filename)
            # do not allow overwriting
            if os.path.exists(path):
                raise DownloadError("Download file already exists: %s" % path)
        elif path:
            # fully qualified file path
            # allow overwriting
            pass
        elif not path:
            raise DownloadError("Empty download file path")

        with contextlib.ExitStack() as stack:
            if not fd:
                fd = open(path, 'wb')
                # only close a file we open
                stack.callback(fd.close)

            r = self._manager.client.request('GET', self.download_url, stream=True)
            stack.callback(r.close)

            bytes_written = 0
            try:
                bytes_total = int(r.headers.get('content-length', None))
            except TypeError:
                bytes_total = None

            if progress_callback:
                # initial callback (0%)
                progress_callback(bytes_written, bytes_total)

            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
                bytes_written += len(chunk)
                if progress_callback:
                    progress_callback(bytes_written, bytes_total)

        return download_filename
