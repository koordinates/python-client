Koordinates Python API Client
=============================

Release v\ |version|. 

A BSD-licensed Python client library for a number of Koordinates web APIs.

The library provides easy access to Koordinates web services, particularly the `Data Administration APIs <https://support.koordinates.com/hc/en-us/sections/200876264-Koordinates-Administration-API>`_.::

    import koordinates

    client = koordinates.Client(host='labs.koordinates.com', token='MY_API_TOKEN')

    # print the 10 most recently created layers
    for layer in client.layers.order_by('created_at')[:10]:
       print(layer)

Features
========

The library aims to reflect the available `Koordinates web APIs <https://support.koordinates.com/hc/en-us/sections/200876264-Koordinates-Administration-API>`_. Currently the following APIs have support in the library:

- `Data Catalog API <https://support.koordinates.com/hc/en-us/articles/204767344-Koordinates-Data-Catalog-API>`_
- `Layers & Tables API <https://support.koordinates.com/hc/en-us/articles/204795824-Koordinates-Layers-Tables-API>`_
- `Sets API <https://support.koordinates.com/hc/en-us/articles/205008090-Koordinates-Sets-API>`_
- `Publishing API <https://support.koordinates.com/hc/en-us/articles/204795854-Koordinates-Publishing-API>`_
- `Licenses API <https://support.koordinates.com/hc/en-us/articles/205008070-Koordinates-License-API>`_
- `Metadata API <https://support.koordinates.com/hc/en-us/articles/204795834-Koordinates-Metadata-API>`_
- `Token API <https://support.koordinates.com/hc/en-us/articles/204890044-Koordinates-Token-API>`_

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

API Documentation
-----------------

 If you are looking for information on a specific function, class or method, this part of the documentation is for you.

 .. toctree::
    :maxdepth: 3

    koordinates

Support
=======

Please report bugs as `Github issues <https://github.com/koordinates/python-client/issues>`__, or see :ref:`user/contributing` below if you wish to suggest an improvement or make a change. For general technical support for the APIs and libraries, please contact us via `support.koordinates.com <https://support.koordinates.com>`_.

