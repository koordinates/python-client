.. _quickstart:

Quick Start
===========
Here's a very short overview of how the library may be used to achieve some
common tasks.

Begin by importing the Requests module::

    >>> import api

Prepare to use the library by making a connection ::

    >>> conn = api.Connection('auser', 'apassword')

Fetch all the Layers objects via a Python generator and iterate over them ::

    >>> # Python 3.x
    >>> for the_layer in conn.layer.get_list().execute_get_list():
    ...     print(the_layer.id)
    >>>
    >>> # Python 2.x
    >>> for the_layer in conn.layer.get_list().execute_get_list():
    ...     print the_layer.id
    >>>

Fetch a filtered set of Layer objects via a Python generator and iterate over them ::

    >>> # Python 3.x
    >>> for the_layer in conn.layer.get_list().filter('Quattroshapes')\
    ...                                       .execute_get_list():
    ...     print(the_layer.name)
    >>>
    >>> # Python 2.x
    >>> for the_layer in conn.layer.get_list().filter('Quattroshapes')\
    ...                                       .execute_get_list():
    ...     print the_layer.name 
    >>>


Fetch a filtered set of Layer objects and specify your own sortation for the returned
objects. Iterate over them using a Python generator::

    >>> # Python 3.x
    >>> for the_layer in conn.layer.get_list().filter('Quattroshapes')\
    ...                                       .order_by('name')\
    ...                                       .execute_get_list():
    ...     print(the_layer.name)
    >>>
    >>> # Python 2.x
    >>> for the_layer in conn.layer.get_list().filter('Quattroshapes')
    ...                                       .order_by('name')
    ...                                       .execute_get_list():
    ...     print the_layer.name 
    >>>

Fetch a single Layer object ::

    >>> # Python 3.x
    >>> # Fetch the Layer with id = 123
    >>> the_layer = conn.layer.get(123)
    >>> print(the_layer.name) 
    ...
    >>> # Python 2.x
    >>> # Fetch the Layer with id = 123
    >>> the_layer = conn.layer.get(123)
    >>> print the_layer.name  
    >>>

Make use of the hierarchy of data within a single object exposed as Python 
class instances via the library ::

    >>> # Python 3.x
    >>> # Fetch the Layer with id = 123 and extract the 
    >>> # data.crs value
    >>> conn.layer.get(123)
    >>> print(conn.layer.data.crs) 
    >>>'EPSG:2193'
    >>> # Python 2.x
    >>> # Fetch the Layer with id = 123 and extract the 
    >>> # data.crs value
    >>> conn.layer.get(123)
    >>> print conn.layer.data.crs 
    >>>'EPSG:2193'
    >>>

Create a Layer from new ::

    >>> # Python 2.x and 3.x
    >>> conn.layer.name = api.Layer()
    >>> conn.layer.name = "A Test Layer" 
    >>> conn.layer.group.id = 999
    >>> conn.layer.group.url = "https://koordinates.com/services/api/v1/groups/{}/".format(conn.layer.group.id)
    >>> conn.layer.group.name = "Foo City Council"
    >>> conn.layer.group.country = "NZ"
    >>> conn.layer.data = api.Data(datasources = [api.Datasource(123456)]) 
    >>> conn.layer.create()

Publish multiple objects of various types ::

    >>> # Python 2.x and 3.x
    >>> # Publish a number of items, in this case one
    >>> # Table and one Layer 
    >>> pr = api.PublishRequest()
    >>> pr.add_layer_to_publish(1111, 9000)
    >>> pr.add_table_to_publish(2222, 9000)
    >>> conn.multi_publish(pr)

Reimport an existing Layer from its previous datasources and create a new version ::

    >>> # Python 2.x and 3.x
    >>> # Take the version with id=9999 of the Layer 
    >>> # with id = 8888 and reimport it 
    >>> conn.version.import_version(8888, 9999)

Publish a specific version of a Layer ::

    >>> # Python 2.x and 3.x
    >>> # Fetch the version with id=9999 of the Layer
    >>> # with id = 8888 and publish it
    conn.version.get(8888, 9999)
    conn.version.publish()

