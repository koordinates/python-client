"""
The `Metadata API <https://help.koordinates.com/api/publisher-admin-api/metadata-api/>`_
provides an interface for adding, inspecting and downloading
XML metadata documents against a range of objects.
"""

from requests_toolbelt.downloadutils import stream

from . import base
from . import exceptions


class MetadataManager(base.InnerManager):
    """
    Accessor for querying and updating metadata.

    Access via the ``metadata`` property of :py:class:`koordinates.layers.Layer`
    or :py:class:`koordinates.sets.Set` instances.
    """

    def set(self, parent_url, fp):
        """
        If the parent object already has XML metadata, it will be overwritten.

        Accepts XML metadata in any of the three supported formats.
        The format will be detected from the XML content.

        The Metadata object becomes invalid after setting

        :param file fp: A reference to an open file-like object which the content will be read from.
        """
        url = parent_url + self.client.get_url_path('METADATA', 'POST', 'set', {})
        r = self.client.request('POST', url, data=fp, headers={'Content-Type': 'text/xml'})
        if r.status_code not in [200, 201]:
            raise exceptions.ServerError("Expected success response, got %s: %s" % (r.status_code, url))


class Metadata(base.InnerModel):
    FORMAT_ISO = 'iso'
    FORMAT_FGDC = 'fgdc'
    FORMAT_DC = 'dc'
    FORMAT_NATIVE = 'native'

    class Meta:
        manager = MetadataManager

    def get_xml(self, fp, format=FORMAT_NATIVE):
        """
        Returns the XML metadata for this source, converted to the requested format.
        Converted metadata may not contain all the same information as the native format.

        :param file fp: A path, or an open file-like object which the content should be written to.
        :param str format: desired format for the output. This should be one of the available
            formats from :py:meth:`.get_formats`, or :py:attr:`.FORMAT_NATIVE` for the native format.

        If you pass this function an open file-like object as the fp parameter, the function will
        not close that file for you.
        """
        r = self._client.request('GET', getattr(self, format), stream=True)
        filename = stream.stream_response_to_file(r, path=fp)
        return filename

    def get_formats(self):
        """ Return the available format names for this metadata """
        formats = []
        for key in (self.FORMAT_DC, self.FORMAT_FGDC, self.FORMAT_ISO):
            if hasattr(self, key):
                formats.append(key)
        return formats
