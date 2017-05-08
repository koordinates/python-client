from __future__ import unicode_literals

import abc
import collections
import datetime
import copy
import itertools
import logging
import re

import six
from six.moves import urllib

from .exceptions import ClientValidationError
from .utils import make_date, is_bound


logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseManager(object):
    """
    Base class for Model Manager classes.

    Instantiated by the Model metaclass and attached to model._meta.manager.
    The Client object needs to set itself on the Manager instance before it's used.
    """

    #_URL_KEY = None
    model = None

    def __init__(self, client):
        self.client = client

    def _meta_attribute(self, attribute, default=None):
        return getattr(self.model._meta, attribute, default)

    def create_from_result(self, result, **kwargs):
        obj = self.model()
        return obj._deserialize(result, self, **kwargs)

    def _get(self, target_url, expand=[]):
        headers = {}
        if expand:
            headers['Expand'] = ','.join(expand)

        r = self.client.request('GET', target_url, headers=headers)
        return self.create_from_result(r.json())

    def _reverse_url(self, url):
        return self.client.reverse_url(self._URL_KEY, url)


@six.add_metaclass(abc.ABCMeta)
class InnerManager(BaseManager):
    def __init__(self, client, parent_manager):
        super(InnerManager, self).__init__(client)
        self.parent = parent_manager


@six.add_metaclass(abc.ABCMeta)
class Manager(BaseManager):
    def list(self):
        """
        Fetches a set of model objects

        :rtype: :py:class:`koordinates.base.Query`
        """
        target_url = self.client.get_url(self._URL_KEY, 'GET', 'multi')
        return Query(self, target_url)

    def get(self, id, expand=[]):
        """Fetches a Model instance determined by the value of `id`.

        :param id: numeric ID for the Model.
        """
        target_url = self.client.get_url(self._URL_KEY, 'GET', 'single', {'id': id})
        return self._get(target_url, expand=expand)

    # Query methods we delegate
    def filter(self, *args, **kwargs):
        """
        Returns a filtered Query view of the model objects.
        Equivalent to calling ``.list().filter(...)``.
        See :py:meth:`koordinates.base.Query.filter`.
        """
        return self.list().filter(*args, **kwargs)

    def order_by(self, *args, **kwargs):
        """
        Returns an ordered Query view of the model objects.
        Equivalent to calling ``.list().order_by(...)``.
        See :py:meth:`koordinates.base.Query.order_by`.
        """
        return self.list().order_by(*args, **kwargs)

    def expand(self, *args, **kwargs):
        """
        Returns an expanded Query view of the model objects.
        Equivalent to calling ``.list().expand()``.
        Using expansions may have significant performance implications for some API requests.
        See :py:meth:`koordinates.base.Query.expand`.
        """
        return self.list().expand(*args, **kwargs)

    def create(self, object):
        # We don't have to have creatable models, so it's not an abstractmethod.
        raise NotImplementedError()


class Query(object):
    """
    Chainable query class to manage GET requests for lists.
    Supports filtering by multiple attributes and sorting, and deals
    with pagination of resultsets into a single iterator.

    Query objects are instantiated by methods on the Manager classes.
    To actually execute the query, iterate over it. You can also call
    len() to return the length - this will do the "first" page request
    and examine the ``X-Resource-Range`` header to produce a count.
    """
    def __init__(self, manager, url, valid_filter_attributes=None, valid_sort_attributes=None):
        self._manager = manager
        self._target_url = url
        self._count = None
        self._filters = collections.defaultdict(list)
        self._order_by = None
        self._expand = None
        self._extra = collections.defaultdict(list)

        self._valid_filter_attrs = self._manager._meta_attribute('filter_attributes', []) if valid_filter_attributes is None else valid_filter_attributes
        self._valid_sort_attrs = self._manager._meta_attribute('ordering_attributes', []) if valid_sort_attributes is None else valid_sort_attributes

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._manager.model.__name__)

    def __str__(self):
        return self._to_url()

    def _request(self, url, method='GET'):
        r = self._manager.client.request(method, url, headers=self._to_headers())
        r.raise_for_status()
        return r

    def _update_range(self, response):
        """ Update the query count property from the `X-Resource-Range` response header """
        header_value = response.headers.get('x-resource-range', '')
        m = re.match(r'\d+-\d+/(\d+)$', header_value)
        if m:
            self._count = int(m.group(1))
        else:
            self._count = None

    def _to_url(self):
        """ Serialises this query into a request-able URL including parameters """
        url = self._target_url

        params = collections.defaultdict(list, copy.deepcopy(self._filters))
        if self._order_by is not None:
            params['sort'] = self._order_by
        for k, vl in self._extra.items():
            params[k] += vl

        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)

        return url

    def _to_headers(self):
        """ Serialises this query into a request-able set of headers """
        headers = {}
        if self._expand:
            headers['Expand'] = 'list'

        return headers

    def _next_url(self, response):
        """
        Return the URL to the next page of results

        Paginate via Link headers
        Link URLs will include the query parameters, so we can use it as an entire URL.
        """
        return response.links.get("page-next", {}).get('url', None)

    def __iter__(self):
        """
        Execute this query and return the results (generally as Model objects)
        """
        if hasattr(self, '_first_page'):
            # if len() has been called on this Query, we have a cached page
            # of results & a next url
            page_results, url = self._first_page
            del self._first_page
        else:
            url = self._to_url()
            r = self._request(url)
            page_results = r.json()

            # Update position
            self._update_range(r)

            # Point to the next page
            url = self._next_url(r)

        for raw_result in page_results:
            yield self._manager.create_from_result(raw_result)

        while url:
            r = self._request(url)
            page_results = r.json()

            # Update position
            self._update_range(r)

            for raw_result in page_results:
                yield self._manager.create_from_result(raw_result)

            # Paginate via Link headers
            # Link URLs will include the query parameters, so we can use it as an entire URL.
            url = r.links.get("page-next", {}).get('url', None)

    def __len__(self):
        """
        Get the count for the query results. If we've previously started iterating we use
        that count, otherwise do a request and look at the ``X-Resource-Range`` header.
        """
        if self._count is None:
            r = self._request(self._to_url())
            self._update_range(r)
            self._first_page = (r.json(), self._next_url(r))
        return self._count

    def __getitem__(self, k):
        """
        Limited slicing support ([N] and [:N] only, for positive N)
        """
        if isinstance(k, int) and k >= 0:
            try:
                return next(itertools.islice(self.__iter__(), k, None))
            except StopIteration:
                raise IndexError(k)

        elif not isinstance(k, slice) \
                or k.start is not None \
                or k.step is not None \
                or k.stop is None \
                or k.stop <= 0:
            raise ValueError("Only query[:+N] or query[+N] slicing is supported.")

        return list(itertools.islice(self.__iter__(), k.stop))

    def _clone(self):
        q = Query(manager=self._manager,
            url=self._target_url,
            valid_filter_attributes=self._valid_filter_attrs,
            valid_sort_attributes=self._valid_sort_attrs
        )

        q._filters = collections.defaultdict(list, copy.deepcopy(self._filters))
        q._order_by = self._order_by
        q._expand = self._expand
        q._extra = collections.defaultdict(list, copy.deepcopy(self._extra))
        return q

    def extra(self, **params):
        """
        Set extra query parameters (eg. filter expressions/attributes that don't validate).
        Appends to any previous extras set.

        :rtype: Query
        """
        q = self._clone()
        for key, value in params.items():
            q._extra[key].append(value)
        return q

    def filter(self, **filters):
        """
        Add a filter to this query.
        Appends to any previous filters set.

        :rtype: Query
        """

        q = self._clone()
        for key, value in filters.items():
            filter_key = re.split('__', key)
            filter_attr = filter_key[0]
            if filter_attr not in self._valid_filter_attrs:
                raise ClientValidationError("Invalid filter attribute: %s" % key)

            # we use __ as a separator in the Python library, the APIs use '.'
            q._filters['.'.join(filter_key)].append(value)
        return q

    def order_by(self, sort_key=None):
        """
        Set the sort for this query. Not all attributes are sorting candidates.
        To sort in descending order, call ``Query.order_by('-attribute')``.

        Calling ``Query.order_by()`` replaces any previous ordering.

        :rtype: Query
        """
        if sort_key is not None:
            sort_attr = re.match(r'(-)?(.*)$', sort_key).group(2)
            if sort_attr not in self._valid_sort_attrs:
                raise ClientValidationError("Invalid ordering attribute: %s" % sort_key)

        q = self._clone()
        q._order_by = sort_key
        return q

    def expand(self):
        """
        Expand list results in this query.
        This can have a performance penalty for some objects.

        :rtype: Query
        """
        q = self._clone()
        q._expand = True
        return q


class ModelMeta(type):
    """
    Sets up the special model characteristics based on the ``Meta:`` object on the model
    """
    def __new__(meta, name, bases, attrs):
        klass = super(ModelMeta, meta).__new__(meta, name, bases, attrs)
        try:
            ModelBase
            Model
            InnerModel
        except NameError:
            # klass is ModelBase/Model/InnerModel, it doesn't have a `Meta:` object
            pass
        else:
            if not hasattr(klass, "Meta"):
                raise AttributeError("Missing Meta object for %s" % klass)

            # Move model.Meta to model._meta
            klass._meta = klass.Meta
            del klass.Meta

            # Associate this model with it's manager
            if getattr(klass._meta.manager, "model") and klass._meta.manager.model is not klass:
                # the manager already has a model!
                if issubclass(klass, klass._meta.manager.model):
                    # this is due to subclassing the model and not the manager
                    # we *don't* add the subclass, we assume you're doing downcasting or
                    # some other cleverness with the subclass, and only querying the superclass.
                    pass
                else:
                    raise TypeError("%s already has an associated model: %s" % (
                        klass._meta.manager.__name__,
                        klass._meta.manager.model.__name__)
                    )
            else:
                klass._meta.manager.model = klass

            # add default accessors for relations
            # class MyModel(Model):
            #     class Meta:
            #         relations = {
            #             'foo': FooModel,    # FK to a single FooModel
            #             'bars': [BarModel], # pointer to multiple BarModel objects
            #         }
            #
            # -> mymodel.get_foo()
            # -> mymodel.list_bars()

            # method factories to workaround late-binding in loops
            def build_multi_getter(r_class, r_attr):
                @is_bound
                def _getter(self):
                    rel_url = getattr(self, r_attr)
                    rel_mgr = self._manager.client.get_manager(r_class)
                    return Query(rel_mgr, rel_url)
                return _getter

            def build_single_getter(r_class, r_attr):
                @is_bound
                def _getter(self):
                    rel_url = getattr(self, r_attr, None)
                    if rel_url:
                        rel_mgr = self._manager.client.get_manager(r_class)
                        return rel_mgr._get(rel_url)
                    else:
                        return None
                return _getter


            for ref_attr, ref_class in getattr(klass._meta, 'relations', {}).items():
                if isinstance(ref_class, (list, tuple)) and len(ref_class) == 1:
                    # multiple relation
                    ref_method = 'list_%s' % ref_attr
                    ref_class = ref_class[0]
                    ref_getter = build_multi_getter(ref_class, ref_attr)
                else:
                    # single relation
                    ref_method = 'get_%s' % ref_attr
                    ref_getter = build_single_getter(ref_class, ref_attr)

                    setattr(klass, ref_method, ref_getter)

                # don't redefine any existing methods
                if not hasattr(klass, ref_method):
                    setattr(klass, ref_method, ref_getter)
                    logger.debug("klass=%s added relation method %s()", klass, ref_method)
        return klass


class SerializableBase(object):
    """
    Base class for simple serialization.
    """

    def __setattr__(self, name, value):
        if isinstance(value, ModelBase) and not name.startswith('_'):
            # set the ._parent attribute on the passed-in Model instance
            object.__setattr__(value, '_parent', self)
        object.__setattr__(self, name, value)

    def _deserialize(self, data):
        """
        Deserialise from JSON response data.

        String items named ``*_at`` are turned into dates.

        Filters out:
        * attribute names in ``Meta.deserialize_skip``

        :param data dict: JSON-style object with instance data.
        :return: this instance
        """
        if not isinstance(data, dict):
            raise ValueError("Need to deserialize from a dict")

        try:
            skip = set(getattr(self._meta, 'deserialize_skip', []))
        except AttributeError:  # _meta not available
            skip = []

        for key, value in data.items():
            if key not in skip:
                value = self._deserialize_value(key, value)
                setattr(self, key, value)
        return self

    def _deserialize_value(self, key, value):
        if key.endswith('_at') and isinstance(value, six.string_types):
            value = make_date(value)
        return value

    def _serialize(self, skip_empty=True):
        """
        Serialise this instance into JSON-style request data.

        Filters out:
        * attribute names starting with ``_``
        * attribute values that are ``None`` (unless ``skip_empty`` is ``False``)
        * attribute values that are empty lists/tuples/dicts (unless ``skip_empty`` is ``False``)
        * attribute names in ``Meta.serialize_skip``
        * constants set on the model class

        Inner :py:class:`Model` instances get :py:meth:`._serialize` called on them.
        Date and datetime objects are converted into ISO 8601 strings.

        :param bool skip_empty: whether to skip attributes where the value is ``None``
        :rtype: dict
        """
        skip = set(getattr(self._meta, 'serialize_skip', []))

        r = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            elif k in skip:
                continue
            elif v is None and skip_empty:
                continue
            elif isinstance(v, (dict, list, tuple, set)) and len(v) == 0 and skip_empty:
                continue
            else:
                r[k] = self._serialize_value(v)
        return r

    def _serialize_value(self, value):
        """
        Called by :py:meth:`._serialize` to serialise an individual value.
        """
        if isinstance(value, (list, tuple, set)):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return dict([(k, self._serialize_value(v)) for k, v in value.items()])
        elif isinstance(value, ModelBase):
            return value._serialize()
        elif isinstance(value, datetime.date):  # includes datetime.datetime
            return value.isoformat()
        else:
            return value


@six.add_metaclass(ModelMeta)
class ModelBase(SerializableBase):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        s = str(getattr(self, "id", None))
        if getattr(self, 'title', None):
            s += " - %s" % self.title
        return s

    def __init__(self, **kwargs):
        self._manager = None
        self.id = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        # is it a Model?
        if not isinstance(other, ModelBase):
            return False

        # is it a child or parent class?
        if not (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)):
            return False

        # am I bound?
        if not hasattr(self, 'id'):
            return False

        # does it's id match mine?
        if getattr(other, 'id', None) != self.id:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def _is_bound(self):
        return bool(getattr(self, 'id', None) is not None \
            and getattr(self, 'url', None) \
            and getattr(self, '_manager', None))

    @property
    def _client(self):
        if not self._manager:
            raise ValueError("%r must be bound to access a Client" % self)
        return self._manager.client

    def _deserialize(self, data, manager):
        """
        Deserialise from JSON response data.

        String items named ``*_at`` are turned into dates.
        Dict items named ``_by`` are turned into Users.

        :param data dict: JSON-style object with instance data.
        :return: this instance
        """
        if not issubclass(self.__class__, manager.model):
            raise TypeError("Manager %s is for %s, expecting %s" % (manager.__class__.__name__, manager.model.__name__, self.__class__.__name__))

        self._manager = manager
        return super(ModelBase, self)._deserialize(data)

    def _deserialize_value(self, key, value):
        from .users import User
        if key.endswith('_by') and isinstance(value, dict):
           value = User()._deserialize(value, self._manager.client.get_manager(User))
        else:
            value = super(ModelBase, self)._deserialize_value(key, value)
        return value


class Model(ModelBase):
    """
    Base class for models with managers.

    Model subclasses need a Meta class, which (in particular)
    links to their Manager class:

        class FooManager(Manager):
            ...

        class Foo(Model):
            class Meta:
                # Manager class
                manager = FooManager
                # Attributes available for ordering
                ordering_attributes = []
                # Attributes available for filtering
                filter_attributes = []
                # For the default implementation of ._serialize(), attributes to skip.
                serialize_skip = []
                # For the default implementation of ._deserialize(), attributes to skip.
                deserialize_skip = []
            ...
    """

    @is_bound
    def refresh(self):
        """
        Refresh this model from the server.

        Updates attributes with the server-defined values. This is useful where the Model
        instance came from a partial response (eg. a list query) and additional details
        are required.

        Existing attribute values will be overwritten.
        """
        r = self._client.request('GET', self.url)
        return self._deserialize(r.json(), self._manager)


class InnerModel(ModelBase):
    """
    Base class for Inner Models.

    These are models that are nested inside attributes of another model,
    and are saved and loaded as part of the parent model.
    """
    def __init__(self, **kwargs):
        self._parent = None
        super(InnerModel, self).__init__(**kwargs)

    @property
    def _is_bound(self):
        return bool(self._parent and self._parent._is_bound)

    @property
    def _client(self):
        return self._parent._client

    def _deserialize(self, data, manager, parent):
        self._parent = parent
        return super(InnerModel, self)._deserialize(data, manager)
