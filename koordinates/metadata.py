"""
The Koordinates Metadata API provides an interface for adding, inspecting
and downloading XML metadata documents against a range of objects.
"""

from . import base


class MetadataManager(base.InnerManager):
    def __init__(self, parent):
        self._parent = parent

class Metadata(base.Model):
    class Meta:
        manager = MetadataManager

    def get_iso_content(self, fp):
        """Returns the XML metadata for this source, converted to the iso format.

        The converted metadata may not contain all the same information as the native format.

        :param fp: A reference to an open file which the content should be written to

        """
        import pdb;pdb.set_trace()
        #target_url = self.meta.manager._parent.get_url(self.URL_KEY, 'GET', 'metadata')
        target_url = self._client.get_url(self.URL_KEY, 'GET', 'metadata')
        obj = self._get(target_url)


