Koordinates Python API Client
=============================

Release v\ |version|.

A BSD-licensed Python client library for a number of `Koordinates <https://koordinates.com>`_ web APIs.

The library provides easy access to Koordinates web services, particularly the `Publisher Admin APIs <https://help.koordinates.com/api/publisher-admin-api/>`_.::

    import koordinates

    client = koordinates.Client(host='labs.koordinates.com', token='MY_API_TOKEN')

    # print the 10 most recently created layers
    for layer in client.layers.order_by('created_at')[:10]:
       print(layer)

Features
========

The library aims to reflect the available `Koordinates web APIs <https://help.koordinates.com/api/publisher-admin-api/>`_. Currently the following APIs have support in the library:

- `Data Catalog API <https://help.koordinates.com/api/publisher-admin-api/data-catalog-api/>`_
- `Layers & Tables API <https://help.koordinates.com/api/publisher-admin-api/layers-tables-api/>`_
- `Sets API <https://help.koordinates.com/api/publisher-admin-api/sets-api/>`_
- `Publishing API <https://help.koordinates.com/api/publisher-admin-api/publishing-api/>`_
- `Licenses API <https://help.koordinates.com/api/publisher-admin-api/license-api/>`_
- `Metadata API <https://help.koordinates.com/api/publisher-admin-api/metadata-api/>`_
- `Token API <https://help.koordinates.com/api/publisher-admin-api/token-api/>`_
- `Data Sources API <https://help.koordinates.com/api/publisher-admin-api/data-sources-api/>`_
- `Permissions API <https://help.koordinates.com/api/publisher-admin-api/permissions-api/>`_
- `Exports API <https://help.koordinates.com/api/publisher-admin-api/export-api/>`_

We're working hard to add support for additional APIs to the library, so expect this list to grow soon.

Compatibility
~~~~~~~~~~~~~

- Python 2.7
- Python 3.3+


User Guide
==========
.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/quickstart
   user/contributing
   api


Support
=======

Please report bugs as `Github issues <https://github.com/koordinates/python-client/issues>`__, or see :doc:`user/contributing` if you wish to suggest an improvement or make a change. For general technical support for the APIs and library, please contact us via `help.koordinates.com <https://support.koordinates.com/hc/en-us/requests/new>`_.

