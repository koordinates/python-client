# -*- coding: utf-8 -*-

"""
koordinates.catalog
===================

The `Data Catalog API <https://help.koordinates.com/api/publisher-admin-api/data-catalog-api/>`_
is a read-only API for listing data from the Koordinates catalog.
For write access to the listed items, refer to the item specific models.

"""
import logging

from . import base
from .layers import Layer, Table
from .sets import Set

logger = logging.getLogger(__name__)


class CatalogManager(base.Manager):
    """
    Accessor for querying across the site via the Catalog API.

    Access via the ``catalog`` property of a :py:class:`koordinates.client.Client` instance.
    """

    _URL_KEY = 'CATALOG'

    def get(self, *args, **kwargs):
        raise NotImplementedError("No support for getting individual items via the Catalog API")

    def list(self):
        """
        The published version of each layer, table, set, document or source.
        If something hasn’t been published yet, it won’t appear here.
        """
        return super(CatalogManager, self).list()

    def _get_item_class(self, url):
        """ Return the model class matching a URL """
        if '/layers/' in url:
            return Layer
        elif '/tables/' in url:
            return Table
        elif '/sets/' in url:
            return Set
        # elif '/documents/' in url:
        #     return Document
        else:
            raise NotImplementedError("No support for catalog results of type %s" % url)

    def create_from_result(self, result):
        try:
            klass = self._get_item_class(result['url'])
            obj = klass()
            return obj._deserialize(result, self.client.get_manager(klass))
        except NotImplementedError:
            # return as dict
            return result

    def list_latest(self):
        """
        A filterable list view of layers, tables, sets, documents and sources, similar to :py:meth:`koordinates.catalog.CatalogManager.list`.
        This returns the latest version of each item, regardless of whether or not it has been published.
        """
        target_url = self.client.get_url(self._URL_KEY, 'GET', 'latest')
        filter_attrs = self.model._meta.filter_attributes + ('version',)
        return base.Query(self, target_url, valid_filter_attributes=filter_attrs)


class CatalogEntry(base.Model):
    class Meta:
        manager = CatalogManager
        filter_attributes = (
            'kind', 'public', 'group', 'license', 'category',
            'geotag', 'tag', 'q', 'created_at', 'updated_at',
        )
        ordering_attributes = ('name', 'created_at', 'updated_at', 'popularity',)

    def __init__(self, **kwargs):
        raise TypeError("CatalogEntry isn't meant to be instantiated")
