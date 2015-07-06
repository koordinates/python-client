# -*- coding: utf-8 -*-

"""
koordinates.publishing
======================

The Group Publishing API allows for draft versions of versioned objects
Documents, Layers, and Tables) to be scheduled for publishing together.
"""

from . import base
from .utils import is_bound


class PublishManager(base.Manager):
    URL_KEY = 'PUBLISH'


class Publish(base.Model):
    """
    The Group Publishing API allows for draft versions of versioned objects
    (Documents, Layers, and Tables) to be scheduled for publishing together.

    A Publish object describes an active publishing group.
    """
    class Meta:
        manager = PublishManager
        attribute_filter_candidates = ('state', 'reference',)

    @is_bound
    def cancel(self):
        """ Cancel a pending publish task """
        target_url = self._client.get_url('PUBLISH', 'DELETE', 'single', {'id': self.id})
        self._client.request('DELETE', target_url)
