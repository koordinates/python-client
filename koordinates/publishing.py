# -*- coding: utf-8 -*-

"""
koordinates.publishing
======================

The `Group Publishing API <https://help.koordinates.com/api/publisher-admin-api/publishing-api/>`_
allows for draft versions of versioned objects Documents,
Layers, and Tables) to be scheduled for publishing together.
"""
import logging

from . import base
from .utils import is_bound


logger = logging.getLogger(__name__)


class PublishManager(base.Manager):
    """
    Accessor for querying Publish groups.

    Access via the ``publishing`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'PUBLISH'

    def create(self, publish):
        """
        Creates a new publish group.
        """
        target_url = self.client.get_url('PUBLISH', 'POST', 'create')
        r = self.client.request('POST', target_url, json=publish._serialize())
        return self.create_from_result(r.json())

class Publish(base.Model):
    """
    Represents an active publishing group.
    """
    class Meta:
        manager = PublishManager
        attribute_filter_candidates = ('state', 'reference',)

    PUBLISH_STRATEGY_TOGETHER = 'together'
    PUBLISH_STRATEGY_INDIVIDUAL = 'individual'

    ERROR_STRATEGY_ABORT = 'abort'
    ERROR_STRATEGY_IGNORE = 'ignore'

    def __init__(self, **kwargs):
        self.items = []
        super(Publish, self).__init__(**kwargs)

    @is_bound
    def cancel(self):
        """ Cancel a pending publish task """
        target_url = self._client.get_url('PUBLISH', 'DELETE', 'single', {'id': self.id})
        r = self._client.request('DELETE', target_url)
        logger.info("cancel(): %s", r.status_code)

    def get_items(self):
        """
        Return the item models associated with this Publish group.
        """
        from .layers import Layer

        # no expansion support, just URLs
        results = []
        for url in self.items:
            if '/layers/' in url:
                r = self._client.request('GET', url)
                results.append(self._client.get_manager(Layer).create_from_result(r.json()))
            else:
                raise NotImplementedError("No support for %s" % url)
        return results

    def add_layer_item(self, layer):
        """
        Adds a Layer to the publish group.
        """
        if not layer.is_draft_version:
            raise ValueError("Layer isn't a draft version")

        self.items.append(layer.latest_version)

    def add_table_item(self, table):
        """
        Adds a Table to the publish group.
        """
        if not table.is_draft_version:
            raise ValueError("Table isn't a draft version")

        self.items.append(table.latest_version)
