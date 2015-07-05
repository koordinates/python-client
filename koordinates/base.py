from __future__ import unicode_literals

import abc
import collections
import datetime
import copy
import itertools
import re

import six
from six.moves import urllib

from .exceptions import NotAValidBasisForOrdering, NotAValidBasisForFiltration
from .utils import make_date


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
    """
    Base class for Model Manager classes.

    Instantiated by the Model metaclass and attached to model._meta.manager.
    The Connection object needs to set itself on the Manager instance before it's used.
    """

    #URL_KEY = None
    model = None

    def __init__(self, connection):
        self.connection = connection

    def _meta_attribute(self, attribute, default=None):
        return getattr(self.model._meta, attribute, default)

    def create_from_result(self, result):
        obj = self.model()
        return obj.deserialize(result, self)

    def list(self, *args, **kwargs):
        """
        Fetches a set of Tokens
        """
        target_url = self.connection.get_url(self.URL_KEY, 'GET', 'multi')
        return Query(self, target_url)

    def get(self, id, expand=[]):
        """Fetches a Token determined by the value of `id`.

        :param id: ID for the new :class:`Token`  object.
        """
        target_url = self.connection.get_url(self.URL_KEY, 'GET', 'single', {'id': id})
        return self._get(target_url, id, expand=expand)

    def _get(self, target_url, id, expand):
        headers = {}
        if expand:
            headers['Expand'] = ','.join(expand)

        r = self.connection.request('GET', target_url, headers=headers)
        return self.create_from_result(r.json())

    # Query methods we delegate
    def filter(self, *args, **kwargs):
        return self.list().filter(*args, **kwargs)
    def order_by(self, *args, **kwargs):
        return self.list().order_by(*args, **kwargs)
    def expand(self, *args, **kwargs):
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
    and examine the X-Resource-Range header to produce a count.
    """
    def __init__(self, manager, url):
        self._manager = manager
        self._target_url = url
        self._count = None
        self._filters = collections.defaultdict(list)
        self._order_by = None
        self._expand = None
        self._extra = collections.defaultdict(list)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._manager.model.__name__)

    def __str__(self):
        return self._to_url()

    def _request(self, url, method='GET'):
        r = self._manager.connection.request(method, url, headers=self._to_headers())
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
        """ Serializes this query into a request-able URL including parameters """
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
        """ Serializes this query into a request-able set of headers """
        headers = {}
        if self._expand:
            headers['Expand'] = 'list'

        return headers

    def __iter__(self):
        """ Execute this query and return the results (generally as Model objects) """
        url = self._to_url()
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
        that count, otherwise do a HEAD request and look at the X-Resource-Range header.
        """
        if self._count is None:
            r = self._request(self._to_url(), method='HEAD')
            self._update_range(r)
        return self._count

    def __getitem__(self, k):
        """ Very limited slicing support ([:N] only) """
        if not isinstance(k, slice) \
                or k.start is not None \
                or k.step is not None \
                or k.stop is None \
                or k.stop <= 0:
            raise ValueError("Only query[:N] slicing is supported.")

        return list(itertools.islice(self.__iter__(), k.stop))

    def _clone(self):
        q = Query(self._manager, self._target_url)
        q._filters = collections.defaultdict(list, copy.deepcopy(self._filters))
        q._order_by = self._order_by
        q._expand = self._expand
        q._extra = collections.defaultdict(list, copy.deepcopy(self._extra))
        return q

    def extra(self, **params):
        """
        Set extra query parameters (eg. filter expressions/attributes that don't validate).
        Appends to any previous extras set.
        """
        q = self._clone()
        for key, value in params.items():
            q._extra[key].append(value)
        return q

    def filter(self, **filters):
        """
        Add a filter to this query.
        Appends to any previous filters set.
        """

        q = self._clone()
        for key, value in filters.items():
            filter_key = re.split('__', key)
            filter_attr = filter_key[0]
            if filter_attr not in self._manager._meta_attribute('filter_attributes', []):
                raise NotAValidBasisForFiltration(key)

            # we use __ as a separator in the Python library, the APIs use '.'
            q._filters['.'.join(filter_key)].append(value)
        return q

    def order_by(self, sort_key=None):
        """
        Set the sort for this query. Not all attributes are sorting candidates.
        To sort in descending order, call `Query.order_by('-attribute')`.

        Calling `Query.order_by()` replaces any previous ordering.
        """
        if sort_key is not None:
            sort_attr = re.match(r'(-)?(.*)$', sort_key).group(2)
            if sort_attr not in self._manager._meta_attribute('ordering_attributes', []):
                raise NotAValidBasisForOrdering(sort_key)

        q = self._clone()
        q._order_by = sort_key
        return q

    def expand(self):
        """
        Expand list results in this query.
        This can have a performance penalty for
        """
        q = self._clone()
        q._expand = True
        return q


class ModelMeta(type):
    """
    Sets up the special model characteristics based on the `Meta:` object on the model
    """
    def __new__(meta, name, bases, attrs):
        klass = super(ModelMeta, meta).__new__(meta, name, bases, attrs)
        try:
            Model
        except NameError:
            # klass is Model, it doesn't have a `Meta:` object
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
                # this is probably due to subclassing the model and not the manager
                # which isn't supported yet. You need to subclass the manager too.
                raise TypeError("%s already has an associated model: %s" % (
                    klass._meta.manager.__name__,
                    klass._meta.manager.model.__name__)
                )
            else:
                klass._meta.manager.model = klass
        return klass


@six.add_metaclass(ModelMeta)
class Model(object):
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
            # For the default implementation of .serialize(), attributes to skip.
            serialize_skip = []
        ...
    """
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        s = str(self.id)
        if getattr(self, 'title', None):
            s += " - %s" % self.title
        return s

    def __init__(self, **kwargs):
        self._manager = None
        self.id = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def _connection(self):
        return self._manager.connection

    def deserialize(self, data, manager):
        """
        Deserialise from JSON response data.

        String items named ``*_at`` are turned into dates.
        Dict items named ``_by`` are turned into Users.

        :param data dict: JSON-style object with instance data.
        :return: this instance
        """
        from .users import User

        if not isinstance(data, dict):
            raise ValueError("Need to deserialize from a dict")

        self._manager = manager

        for k, v in data.items():
            if k.endswith('_at') and isinstance(v, six.string_types):
                v = make_date(v)
            elif k.endswith('_by') and v:
               v = User().deserialize(v, manager)

            setattr(self, k, v)
        return self

    def serialize(self, skip_empty=True):
        """
        Serialise this instance into JSON-style request data.

        Filters out:
        * attribute names starting with ``_``
        * attribute values that are ``None`` (unless ``skip_empty`` is ``False``)
        * attribute values that are empty lists/tuples/dicts (unless ``skip_empty`` is ``False``)
        * attribute names in ``Meta.serialize_skip``
        * a default set of attribute names (overrideable via ``Meta.serialize_skip_base=[]``):
            - ``id``
            - ``url``
            - ``created_at``, ``deleted_at``
            - ``created_by``, ``deleted_by``

        Inner :py:class:`Model` instances get :py:meth:`serialize` called on them.
        Date and datetime objects are converted into ISO 8601 strings.

        :param bool skip_empty: whether to skip attributes where the value is ``None``
        :rtype: dict
        """
        SERIALIZE_SKIP_DEFAULT = (
            'id',
            'url',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by',
        )
        skip_base = set(getattr(self._meta, 'serialize_skip_base', SERIALIZE_SKIP_DEFAULT))
        skip = set(getattr(self._meta, 'serialize_skip', [])) | skip_base

        r = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            elif k in skip:
                continue
            elif v is None and skip_empty:
                continue
            elif isinstance(v, (dict, list, tuple)) and len(v) == 0 and skip_empty:
                continue
            else:
                r[k] = self._serialize_value(v)
        return r

    def _serialize_value(self, value):
        """
        Called by :py:meth:`serialize` to serialise an individual value.
        """
        if isinstance(value, (list, tuple)):
            return map(self._serialize_value, value)
        elif isinstance(value, dict):
            return dict([(k, self._serialize_value(v)) for k, v in value.items()])
        elif isinstance(value, Model):
            return value.serialize()
        elif isinstance(value, datetime.date):  # includes datetime.datetime
            return value.isoformat()
        else:
            return value
