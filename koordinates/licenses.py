# -*- coding: utf-8 -*-

"""
koordinates.licenses
===================

The Koordinates License API provides access to licenses that can be applied to
layers, tables, sources and documents. It provides access to Creative Commons API
by property lookup, as well as custom and built-in licenses.
"""

from . import base


class LicenseManager(base.Manager):
    URL_KEY = 'LICENSE'

    def get_creative_commons(self, slug, jurisdiction):
        """Returns the Creative Commons license for the given attributes.

        :param str slug: the type of Creative Commons license. It must start with
            ``cc-by`` and can optionally contain ``nc`` (non-commercial),
            ``sa`` (share-alike), ``nd`` (no derivatives) terms, seperated by
            hyphens. Note that a CC license cannot be both ``sa`` and ``nd``
        :param str jurisdiction: The jurisdiction for a ported Creative Commons
            license (eg. ``nz``)
        :rtype: License
        """
        target_url = self.connection.get_url(self.URL_KEY, 'GET', 'cc', {'slug': slug, 'jurisdiction': jurisdiction})
        return self._get(target_url)


class License(base.Model):
    """
    Licenses that can be applied to layers, tables, sources, and documents.
    """
    class Meta:
        manager = LicenseManager
