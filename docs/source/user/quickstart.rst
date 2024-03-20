.. _quickstart:

Quick Start
===========

In this guide, we provide a very short overview of how the library may be used to achieve some
common tasks.

Before you begin, you'll need to know the Koordinates site you're accessing (eg. `labs.koordinates.com <https://labs.koordinates.com>`_), and have a valid API token for the site, created with the scopes you need for the APIs you're using. See `Authentication`_ for more information. You'll also need sufficient permissions on the site to take actions (for example, creating a Layer).

First, import the Koordinates module::

    >>> import koordinates

Prepare to use the library by creating a client::

    >>> client = koordinates.Client('labs.koordinates.com', 'MY_API_TOKEN')

Fetch all the Layer objects via the `Layers & Tables API <https://help.koordinates.com/api/publisher-admin-api/layers-tables-api/>`_ and iterate over them::

    >>> for layer in client.layers.list():
    ...     print(layer.id)
    >>>

Fetch filtered and sorted Layer objects via the `Data Catalog API <https://help.koordinates.com/api/publisher-admin-api/data-catalog-api/>`_ and iterate over them::

    >>> for layer in client.catalog.list().filter(license__type='cc')\
    ...                                   .filter(type='layer')\
    ...                                   .order_by('created_at'):
    ...     print(layer.title)
    >>>

The results of ``.list()`` returns a :py:class:`Query` object which is chainable. It will only make an API request once it gets iterated over or :py:func:`len` is called on it.

Fetch a single Layer object::

    >>> # Fetch the Layer with id = 123
    >>> layer = client.layers.get(123)
    >>> print(layer.title) 
    >>>

Make use of the hierarchy of data within a single object exposed as Python 
class instances via the library::

    >>> # Fetch the Layer with id = 123 and extract the 
    >>> # data.crs value
    >>> layer = client.layers.get(123)
    >>> print(layer.data.crs) 
    >>>EPSG:2193

Create a new Layer from existing datasources::

    >>> layer = koordinates.Layer()
    >>> layer.title = "A Test Layer"
    >>> layer.group = 999
    >>> layer.data = koordinates.layers.LayerData(datasources=[123456])
    >>> layer = client.layers.create(layer)
    >>> print(layer.url)

Publish multiple objects of various types::

    >>> # Publish a number of items, in this case one
    >>> # Table and one Layer 
    >>> publish = koordinates.publishing.Publish()
    >>> publish.add_layer_item(layer)
    >>> publish.strategy = publish.PUBLISH_STRATEGY_TOGETHER
    >>> publish = client.publishing.create(publish)
    >>> print(publish.url)

Reimport an existing Layer from its previous data sources and create a new version::

    >>> # Take the layer with id=8888 and reimport it
    >>> layer = client.layers.get(8888)
    >>> layer = layer.start_update()

Publish a specific version of a Layer::

    >>> # Fetch the version with id=9999 of the Layer
    >>> # with id = 8888 and publish it
    >>> layer_version = client.layers.get(8888).get_version(9999)
    >>> layer_version.publish()


Authentication
==============

To create an API token, visit the 'APIs and Web Services' page under your user menu on the site you want a token for.

Once you have an API token, you can either pass it into the :py:class:`koordinates.client.Client` object when you create it, or set it in the ``KOORDINATES_TOKEN`` environment variable. ::

    # Pass token explicitly
    client = koordinates.Client(host='labs.koordinates.com', token='abcdef1234567890abcdef')

    # Token from environment variable KOORDINATES_TOKEN
    client = koordinates.Client(host='labs.koordinates.com')

Tokens are specific to a Koordinates site. For example, a token created for ``labs.koordinates.com`` wouldn't be valid for another site, such as ``koordinates.com``.

Tokens need to be `created with scopes appropriate <https://help.koordinates.com/api/publisher-admin-api/token-api/>`_ for the APIs you are utilising. For example, to query Sets you need a token with the ``sets:read`` scope, and to create or update a Set you need a token with the ``sets:write`` scope.

If a required scope isn't associated with the token, you will receive an :py:exc:`koordinates.exceptions.InvalidTokenScope` exception.

In addition to the scopes, the user or group owner of the token needs appropriate permissions for the actions they're attempting to take - for example, viewing a particular Set.

If required permissions aren't present, you will receive a :py:exc:`koordinates.exceptions.Forbidden` exception.


Pagination
==========

The library handles pagination of the results of ``.list()`` and related methods. These methods all act as generators and transparently fetch subsequent pages of results from the APIs in the background during iteration.


Limiting Results
================

Limiting the results of ``.list()`` and related methods is available via the python slicing syntax. Only the ``[:N]`` slicing style is supported. For example::

    # Limit to a maximum of three results
    for layer in client.layers.list()[:3]:
        print(layer)


Counting Results
================

In order to count the results of a query or list, use ``len()``. For example: ::

    print(len(client.layers.list()))
    print(len(client.layers.filter(license='cc')))

This will perform a HEAD request unless a request has already been made (via a previous call to ``len()`` or iteration over the results), in which case the previous cached value will be returned.


Result Expansion
================

To prevent additional API requests, you can get the API to expand some relations and levels of detail in responses. 

Not all properties or relations can be expanded. Refer to the Koordinates API documentation for details.

**Important:** Using expansions may have significant performance implications for some API requests.

To expand results in a list request::

    for object in client.catalog.list().expand():
        # object will be a detailed model instance with
        # a full set of attributes
        print(object)

To expand an attribute in a get request::

    set = client.sets.get(id=123, expand='items')
    # the following get_items() call will use the .expand() results
    # instead of making an additional request.
    print(set, len(set.get_items()))
