

Developer Interface
===================
.. module:: koordinates


Some blurb around the interfaces available.

Available Methods
-----------------

.. autofunction:: utils.dump_class_attributes_to_dict
.. autofunction:: utils.is_empty_list
.. autofunction:: utils.make_date
.. autofunction:: utils.make_date_if_possible
.. autofunction:: utils.make_date_list_from_string_list
.. autofunction:: utils.make_list_of_Categories
.. autofunction:: utils.make_list_of_Datasources
.. autofunction:: utils.make_list_of_Fields
.. autofunction:: utils.remove_empty_from_dict


Exceptions
----------
.. autoexception:: exceptions.AttributeNameIsReserved
.. autoexception:: exceptions.FilterMustNotBeSpaces
.. autoexception:: exceptions.ImportEncounteredUpdateConflict
.. autoexception:: exceptions.InvalidAPIVersion
.. autoexception:: exceptions.InvalidPublicationResourceList
.. autoexception:: exceptions.InvalidURL
.. autoexception:: exceptions.KoordinatesException
.. autoexception:: exceptions.KoordinatesValueException
.. autoexception:: exceptions.NotAValidBasisForFiltration
.. autoexception:: exceptions.NotAValidBasisForOrdering
.. autoexception:: exceptions.NotAuthorised
.. autoexception:: exceptions.OnlyOneFilterAllowed
.. autoexception:: exceptions.OnlyOneOrderingAllowed
.. autoexception:: exceptions.PublishAlreadyStarted
.. autoexception:: exceptions.RateLimitExceeded
.. autoexception:: exceptions.ServerTimeOut
.. autoexception:: exceptions.UnexpectedServerResponse

Classes
-------------------
.. autoclass:: connection.Connection
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Version   
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Group     
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Data
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Datasource
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Category
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Autoupdate
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Createdby
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.License 
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Versioninstance 
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Metadata
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Field    
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: layer.Layer   
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: publish.Publish
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: publish.PublishRequest
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: set.Set       
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: api.KData     
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: mixins.KoordinatesURLMixin
    :members:
    :private-members:
    :undoc-members:
.. autoclass:: mixins.KoordinatesObjectMixin
    :members:
    :private-members:
    :undoc-members:
