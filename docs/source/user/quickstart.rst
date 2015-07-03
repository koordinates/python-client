.. _quickstart:

Quick Start
===========
Here's a very short overview of how the library may be used to achieve some
common tasks.

First off, you need to know the koordinates site you're accessing (eg. https://labs.koordinates.com), and have a valid API token for the site, created with the scopes you need for the APIs you're using. See `Authentication`_ for more information. You also need permissions on the site to take the actions.

Begin by importing the Koordinates module::

    >>> from koordinates import api

Prepare to use the library by making a connection ::

    >>> client = api.Client('labs.koordinates.com', 'MY_API_TOKEN')

Fetch all the Layer objects via the `Layers & Tables API <https://support.koordinates.com/hc/en-us/articles/204795824-Koordinates-Layers-Tables-API#layers-&-tables-api-layers-&-tables-list>`_ and iterate over them ::

    >>> for layer in client.layers.list():
    ...     print(layer.id)
    >>>

Fetch filtered and sorted Layer objects via the `Data Catalog API <https://support.koordinates.com/hc/en-us/articles/204767344-Koordinates-Data-Catalog-API>`_ and iterate over them ::

    >>> for layer in client.data.list().filter(license__type='cc')\
    ...                                    .filter(type='layer')\
    ...                                    .order_by('created_at'):
    ...     print(layer.title)
    >>>


Fetch a single Layer object ::

    >>> # Fetch the Layer with id = 123
    >>> layer = client.layer.get(123)
    >>> print(layer.title) 
    >>>

Make use of the hierarchy of data within a single object exposed as Python 
class instances via the library ::

    >>> # Fetch the Layer with id = 123 and extract the 
    >>> # data.crs value
    >>> layer = client.layer.get(123)
    >>> print(layer.data.crs) 
    >>>EPSG:2193

Create a new Layer from existing datasources::

    >>> layer = koordinates.Layer()
    >>> layer.name = "A Test Layer" 
    >>> layer.group = 999
    >>> layer.data = koordinates.LayerData(datasources=[123456]) 
    >>> layer = client.layers.create(layer)
    >>> print(layer.url)

Publish multiple objects of various types ::

    >>> # Publish a number of items, in this case one
    >>> # Table and one Layer 
    >>> publish = koordinates.publishing.Publish()
    >>> publish.add_layer_version(1111)
    >>> publish.add_table_version(2222)
    >>> publish.strategy = publish.STRATEGY_TOGETHER
    >>> publish = client.publishing.create(publish)
    >>> print(publish.url)

Reimport an existing Layer from its previous datasources and create a new version ::

    >>> # Take the version with id=9999 of the Layer 
    >>> # with id = 8888 and reimport it 
    >>> layer = client.layers.get(9999)
    >>> layer = layer.reimport()

Publish a specific version of a Layer ::

    >>> # Fetch the version with id=9999 of the Layer
    >>> # with id = 8888 and publish it
    >>> layer_version = client.layers.get(8888).get_version(9999)
    >>> layer_version.publish()

