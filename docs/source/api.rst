

Developer Interface
===================
.. module:: koordinates


Some blurb around the interfaces available.

Classes
-------------------
.. autoclass:: koordinates.client.Client
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.Layer     
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.LayerManager     
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.LayerVersion   
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.LayerVersionManager   
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.LayerData      
    :members:
    :undoc-members:
.. autoclass:: koordinates.layers.LayerDataManager      
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.BaseManager
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.InnerManager
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.Manager
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.Query
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.ModelMeta
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.Model
    :members:
    :undoc-members:
.. autoclass:: koordinates.base.InnerModel
    :members:
    :undoc-members:

.. autoclass:: koordinates.catalog.CatalogEntry  
    :members:
    :undoc-members:

.. autoclass:: koordinates.catalog.CatalogManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.licenses.LicenseManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.licenses License
    :members:
    :undoc-members:

.. autoclass:: koordinates.metadata.MetadataManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.metadata.Metadata(base.InnerModel):
    :members:
    :undoc-members:

.. autoclass:: koordinates.publishing.PublishManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.publishing.Publish
    :members:
    :undoc-members:

.. autoclass:: koordinates.sets.SetManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.sets.Set
    :members:
    :undoc-members:

.. autoclass:: koordinates.tokens.TokenManager
    :members:
    :undoc-members:

.. autoclass:: koordinates.tokens.Token
    :members:
    :undoc-members:

 
.. autoclass:: koordinates.users.UserManager
    :members:
    :undoc-members:
.. autoclass:: koordinates.users.User
    :members:
    :undoc-members:
.. autoclass:: koordinates.users.GroupManager
    :members:
    :undoc-members:
.. autoclass:: koordinates.users.Group
    :members:
    :undoc-members:

Available Methods
-----------------

.. autofunction:: utils.is_bound
.. autofunction:: utils.make_date


Exceptions
----------
.. autoexception:: exceptions.KoordinatesException
.. autoexception:: exceptions.ClientError
.. autoexception:: exceptions.ClientValidationError
.. autoexception:: exceptions.InvalidAPIVersion
.. autoexception:: exceptions.ServerError
.. autoexception:: exceptions.BadRequest
.. autoexception:: exceptions.AuthenticationError
.. autoexception:: exceptions.Forbidden
.. autoexception:: exceptions.NotFound
.. autoexception:: exceptions.NotAllowed
.. autoexception:: exceptions.Conflict
.. autoexception:: exceptions.RateLimitExceeded
.. autoexception:: exceptions.InternalServerError
.. autoexception:: exceptions.ServiceUnvailable



