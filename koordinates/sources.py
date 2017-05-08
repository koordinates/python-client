# -*- coding: utf-8 -*-

"""
koordinates.sources
===================

The `Data Sources API <https://help.koordinates.com/api/publisher-admin-api/data-sources-api/>`_
provides read+write access to sources, datasources and scans.

A source points to a place where Koordinates can get data from. Sources can contain any number of datasources.

A datasource is a single dataset from a source. One or more datasources may be imported to create a layer,
table or document.

A scan examines a source to find out about what datasources the source provides. Until a source is scanned
it may appear to have no datasources.
"""
import collections
import json
import logging
import mimetypes
import os

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import six

from . import base
from .exceptions import ClientValidationError
from .metadata import Metadata, MetadataManager
from .permissions import PermissionObjectMixin
from .users import Group, User
from .utils import is_bound


logger = logging.getLogger(__name__)


class SourceManager(base.Manager):
    """
    Accessor for querying Sources.

    Access via the ``sources`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'SOURCE'

    def __init__(self, client):
        super(SourceManager, self).__init__(client)
        # Inner model managers
        self._metadata = MetadataManager(client, self)

    def create(self, source, upload_progress_callback=None):
        """
        Creates a new source.

        :param str source: The populated Source object to create.
        :param function upload_progress_callback: For an UploadSource object, an optional callback
                    function which receives upload progress notifications. The function should take two
                    arguments: the number of bytes sent, and the total number of bytes to send.
        :rtype: Source
        """
        # Delegate to the class itself
        return source._create(self, callback=upload_progress_callback)

    def list_datasources(self, source_id):
        """
        Filterable list of Datasources for a Source.
        """
        target_url = self.client.get_url('DATASOURCE', 'GET', 'multi', {'source_id': source_id})
        return base.Query(self.client.get_manager(Datasource), target_url)

    def get_datasource(self, source_id, datasource_id):
        """
        Get a Datasource object

        :rtype: Datasource
        """
        target_url = self.client.get_url('DATASOURCE', 'GET', 'single', {'source_id': source_id, 'datasource_id': datasource_id})
        return self.client.get_manager(Datasource)._get(target_url)

    def list_scans(self, source_id=None):
        """
        Filterable list of Scans for a Source.
        Ordered newest to oldest by default
        """
        if source_id:
            target_url = self.client.get_url('SCAN', 'GET', 'multi', {'source_id': source_id})
        else:
            target_url = self.client.get_ulr('SCAN', 'GET', 'all')
        return base.Query(self.client.get_manager(Scan), target_url)

    def get_scan(self, source_id, scan_id):
        """
        Get a Scan object

        :rtype: Scan
        """
        target_url = self.client.get_url('SCAN', 'GET', 'single', {'source_id': source_id, 'scan_id': scan_id})
        return self.client.get_manager(Scan)._get(target_url)

    def get_scan_log_lines(self, source_id, scan_id):
        """
        Get the log text for a Scan

        :rtype: Iterator over log lines.
        """
        return self.client.get_manager(Scan).get_log_lines(source_id=source_id, scan_id=scan_id)

    def start_scan(self, source_id):
        """
        Start a new scan of a Source.

        :rtype: Scan
        """
        target_url = self.client.get_url('SCAN', 'POST', 'create', {'source_id': source_id})
        r = self.client.request('POST', target_url, json={})
        return self.client.get_manager(Scan).create_from_result(r.json())


class Source(base.Model, PermissionObjectMixin):
    """
    A source points to a place where Koordinates can get data from. Sources can contain any number
    of datasources.
    """
    class Meta:
        manager = SourceManager
        relations = {
            'scans': ['Scan'],
            'datasources': ['Datasource'],
        }
        serialize_skip = ('permissions',)
        deserialize_skip = ('permissions',)

    TYPE_INFO = 'info'
    TYPE_UPLOAD = 'upload'
    TYPE_CIFS = 'cifs'
    TYPE_ARCGIS = 'arcgis'
    TYPE_WFS = 'wfs'
    TYPE_POSTGRES = 'postgres'

    def __init__(self, **kwargs):
        self.items = []
        super(Source, self).__init__(**kwargs)

    def _deserialize(self, data, manager):
        super(Source, self)._deserialize(data, manager)
        self.group = Group()._deserialize(data["group"], manager.client.get_manager(Group)) if data.get("group") else None
        self.user = User()._deserialize(data["user"], manager.client.get_manager(User)) if data.get("user") else None
        self.metadata = Metadata()._deserialize(data["metadata"], manager._metadata, self) if data.get("metadata") else None
        return self

    def _create(self, manager, *args, **kwargs):
        target_url = manager.client.get_url('SOURCE', 'POST', 'create')
        r = manager.client.request('POST', target_url, json=self._serialize())
        return manager.create_from_result(r.json())

    @is_bound
    def save(self, with_data=False):
        """
        Edits this Source
        """
        r = self._client.request('PUT', self.url, json=self._serialize(with_data=with_data))
        return self._deserialize(r.json(), self._manager)

    @is_bound
    def delete(self):
        """ Delete this source """
        r = self._client.request('DELETE', self.url)
        logger.info("delete(): %s", r.status_code)

    @is_bound
    def get_datasource(self, datasource_id):
        return self._manager.get_datasource(self.id, datasource_id)

    @is_bound
    def list_datasources(self):
        return self._manager.list_datasources(self.id)

    @is_bound
    def list_scans(self):
        return self._manager.list_scans(self.id)

    @is_bound
    def get_latest_scan(self):
        results = self._manager.list_scans(self.id).expand()[:1]
        if results:
            return results[0]

    @is_bound
    def get_scan(self, scan_id):
        return self._manager.get_scan(self.id, scan_id)


class UploadSource(Source):
    """
    Subclass of Source used for uploads of files and archives, which are automatically scanned.

    :Example:

    >>> upload = koordinates.UploadSource()
    >>> upload.user = 5
    >>> upload.title = "upload_source example"
    >>> upload.add_file('/path/to/data.zip')
    >>> upload = client.sources.create(upload)

    """
    class Meta:
        manager = SourceManager

    def __init__(self, *args, **kwargs):
        super(UploadSource, self).__init__(*args, **kwargs)
        self.type = self.TYPE_UPLOAD
        self._files = collections.OrderedDict()

    def _create(self, manager, callback=None):
        if self.type != self.TYPE_UPLOAD:
            raise ClientValidationError("Model/type mismatch")

        fields = {
            'source': (None, json.dumps(self._serialize()), 'application/json'),
        }

        def wrapped_callback(monitor):
            callback(monitor.bytes_read, monitor.len)

        opened_files = []
        try:
            for i, (upload_path, (file_or_path, content_type)) in enumerate(self._files.items()):
                if isinstance(file_or_path, six.string_types):
                    # path
                    fp = open(file_or_path, 'rb')
                    opened_files.append(fp)
                else:
                    # file-like object
                    fp = file_or_path

                field = [
                    upload_path,
                    fp,
                ]

                if content_type:
                    field.append(content_type)

                fields['file%d' % i] = tuple(field)

            target_url = manager.client.get_url('SOURCE', 'POST', 'create')
            e = MultipartEncoder(fields=fields)
            m = MultipartEncoderMonitor(e, wrapped_callback if callback else None)

            r = manager.client.request('POST', target_url, data=m, headers={'Content-Type': m.content_type})
        finally:
            for fp in opened_files:
                fp.close()

        return manager.create_from_result(r.json())

    def add_file(self, fp, upload_path=None, content_type=None):
        """
        Add a single file or archive to upload.

        To add metadata records with a file, add a .xml file with the same upload path basename
        eg. ``points-with-metadata.geojson`` & ``points-with-metadata.xml``
        Datasource XML must be in one of these three formats:

          - ISO 19115/19139
          - FGDC CSDGM
          - Dublin Core (OAI-PMH)

        :param fp: File to upload into this source, can be a path or a file-like object.
        :type fp: str or file
        :param str upload_path: relative path to store the file as within the source (eg. ``folder/0001.tif``). \
                                By default it will use ``fp``, either the filename from a path or the ``.name`` \
                                attribute of a file-like object.
        :param str content_type: Content-Type of the file. By default it will attempt to auto-detect from the \
                                 file/upload_path.
        """
        if isinstance(fp, six.string_types):
            # path
            if not os.path.isfile(fp):
                raise ClientValidationError("Invalid file: %s", fp)
            if not upload_path:
                upload_path = os.path.split(fp)[1]
        else:
            # file-like object
            if not upload_path:
                upload_path = os.path.split(fp.name)[1]

        content_type = content_type or mimetypes.guess_type(upload_path, strict=False)[0]
        if upload_path in self._files:
            raise ClientValidationError("Duplicate upload path: %s" % upload_path)

        self._files[upload_path] = (fp, content_type)
        logger.debug("UploadSource.add_file: %s -> %s (%s)", repr(fp), upload_path, content_type)


class ScanManager(base.Manager):
    _URL_KEY = 'SCAN'

    def get_log_lines(self, source_id, scan_id):
        """
        Get the log text for a scan object
        :rtype: Iterator over log lines.
        """
        target_url = self.client.get_url('SCAN', 'GET', 'log', {'source_id': source_id, 'scan_id': scan_id})
        r = self.client.request('GET', target_url, headers={'Accept': 'text/plain'}, stream=True)
        return r.iter_lines(decode_unicode=True)


class Scan(base.Model):
    """
    A scan operation examines a source to find out about what datasources the source provides.
    """

    class Meta:
        manager = ScanManager
        relations = {
            'source': Source,
        }
        filter_attributes = (
            'status', 'started_at', 'completed_at',
        )
        ordering_attributes = (
            'id', 'started_at', 'completed_at',
        )

    @is_bound
    def cancel(self):
        """
        Cancel a running Scan.
        """
        r = self._client.request('DELETE', self.url)
        logger.info("Scan:cancel(): %s", r.status_code)

    @is_bound
    def get_log_lines(self):
        """
        Get the log text for a scan object

        :rtype: Iterator over log lines.
        """
        rel = self._client.reverse_url('SCAN', self.url)
        return self._manager.get_log_lines(**rel)


class DatasourceManager(base.Manager):
    _URL_KEY = 'DATASOURCE'

    def __init__(self, client):
        super(DatasourceManager, self).__init__(client)
        # Inner model managers
        self._metadata = MetadataManager(client, self)


class Datasource(base.Model):
    """
    A datasource is a single dataset from a source. One or more datasources may be imported to create a layer,
    table or document.
    """

    class Meta:
        manager = DatasourceManager
        relations = {
            'source': Source,
        }

    def _deserialize(self, data, manager):
        super(Datasource, self)._deserialize(data, manager)
        self.metadata = Metadata()._deserialize(data["metadata"], manager._metadata, self) if data.get("metadata") else None
        return self
