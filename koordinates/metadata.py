"""
The Koordinates Metadata API provides an interface for adding, inspecting
and downloading XML metadata documents against a range of objects.
"""

from . import base


class MetadataManager(base.InnerManager):
    pass


class Metadata(base.Model):
    class Meta:
        manager = MetadataManager
