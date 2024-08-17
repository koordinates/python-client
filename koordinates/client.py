# -*- coding: utf-8 -*-

"""
koordinates.client
==================
"""

import copy
import json
import logging
import os
import re
import sys
from urllib.parse import urlparse

try:
    from importlib.metadata import version as _version
except ImportError:
    # python < 3.8
    from importlib_metadata import version as _version

import requests
import requests_toolbelt

from . import layers, licenses, publishing, sets, users, catalog, sources, exports
from . import exceptions


logger = logging.getLogger(__name__)


class Client(object):
    """
    A `Client` is used to define the host and api-version which the user
    wants to connect to. The user identity is also defined when `Client`
    is instantiated.
    """

    def __init__(
        self,
        host,
        token=None,
        activate_logging=False,
        api_version="v1",
        url_version=None,
    ):
        """
        :param str host: the domain name of the Koordinates site to connect to (eg. ``labs.koordinates.com``)
        :param str token: Koordinates API token to use for authentication
        :param bool activate_logging: if True then logging to stderr is activated
        :param str api_version: API version of Koordinates site to connect to. Defaults to 'v1'.
        :param str url_version:
            API Version shown in the URLs of the Koordinates site to connect to. This may be differ from the
            `api_version`; for example, the `api_version` may be 'v1`, but the `url_version` may be 'v1.x'.
            If `None`, `url_version` is set to equal `api_version`. Defaults to `None`.
        """
        if activate_logging:
            logging.basicConfig(
                stream=sys.stderr,
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)s %(module)s %(message)s",
            )

        logger.debug("Initializing Client object for %s", host)

        self.host = host
        self.api_version = api_version
        self.url_version = url_version or self.api_version

        if token:
            self.token = token
        elif "KOORDINATES_TOKEN" in os.environ:
            self.token = os.environ["KOORDINATES_TOKEN"]
        else:
            raise KeyError(
                "No authentication token specified, and KOORDINATES_TOKEN not available in the environment."
            )

        self._user_agent = requests_toolbelt.user_agent(
            "KoordinatesPython", _version("koordinates")
        )

        self._init_managers(
            public={
                "sets": sets.SetManager,
                "publishing": publishing.PublishManager,
                "layers": layers.LayerManager,
                "tables": layers.TableManager,
                "licenses": licenses.LicenseManager,
                "catalog": catalog.CatalogManager,
                "sources": sources.SourceManager,
                "exports": exports.ExportManager,
            },
            private=(
                users.GroupManager,
                users.UserManager,
                sources.ScanManager,
                sources.DatasourceManager,
                exports.CropFeatureManager,
                exports.CropLayerManager,
            ),
        )

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": self._user_agent,
            }
        )
        if self.token:
            self._session.headers["Authorization"] = "key {token}".format(
                token=self.token
            )

        super(self.__class__, self).__init__()

    def _init_managers(self, public, private):
        self._manager_map = {}
        for manager_class in private:
            mgr = manager_class(self)
            self._register_manager(mgr.model, mgr)

        for alias, manager_class in list(public.items()):
            mgr = manager_class(self)
            self._register_manager(mgr.model, mgr)
            setattr(self, alias, mgr)

    def _register_manager(self, model, manager):
        self._manager_map[model] = manager

    def get_manager(self, model):
        """
        Return the active manager for the given model.
        :param model: Model class to look up the manager instance for.
        :return: Manager instance for the model associated with this client.
        """
        if isinstance(model, str):
            # undocumented string lookup
            for k, m in list(self._manager_map.items()):
                if k.__name__ == model:
                    return m
            else:
                raise KeyError(model)

        return self._manager_map[model]

    def _assemble_headers(self, method, user_headers=None):
        """
        Takes the supplied headers and adds in any which
        are defined at a client level and then returns
        the result.

        :param user_headers: a `dict` containing headers defined at the
                             request level, optional.

        :return: a `dict` instance
        """

        headers = copy.deepcopy(user_headers or {})

        if method not in ("GET", "HEAD"):
            headers.setdefault("Content-Type", "application/json")

        return headers

    def request(self, method, url, *args, **kwargs):
        headers = self._assemble_headers(method, kwargs.pop("headers", {}))
        r = self._raw_request(method, url, headers, *args, **kwargs)

        if method == "POST":
            # If we're posting to an endpoint
            if r.status_code in (requests.codes.created, requests.codes.accepted):
                # and we get a 201/202 response
                if "location" in r.headers:
                    # with a location header
                    logger.info("%s -> %s", r.status_code, r.headers["location"])

                    # follow it and return the results of the GET
                    r2 = self.request("GET", r.headers["location"])
                    r2.parent_response = r
                    return r2

        return r

    def _raw_request(
        self, method, url, headers, *args, allow_xdomain_redirects=False, **kwargs
    ):
        # for the Koordinates library logging, strip auth tokens from log messages
        # and log POST/PUT bodies if we're sending JSON.
        # Get low-level logging via the requests.packages.urllib3 logger.
        if "json" in kwargs:
            logger.info(
                "Request: %s %s headers=%s body=%s",
                method,
                url,
                json.dumps(headers),
                json.dumps(kwargs["json"]),
            )
        else:
            logger.info("Request: %s %s headers=%s", method, url, json.dumps(headers))

        try:
            r = self._session.request(method, url, headers=headers, *args, **kwargs)
            logger.info("Response: %d %s in %s", r.status_code, r.reason, r.elapsed)
            logger.debug("Response: headers=%s", r.headers)
            r.raise_for_status()
            if not allow_xdomain_redirects and not self._is_same_domain(url, r.url):
                raise exceptions.RedirectException(
                    f"Server responded with cross-domain redirect ({url} -> {r.url})"
                )
            return r
        except requests.HTTPError as e:
            logger.warning("Response: %s: %s", e, r.text)
            raise exceptions.ServerError.from_requests_error(e)
        except requests.RequestException as e:
            raise exceptions.ServerError.from_requests_error(e)

    def _is_same_domain(self, url1, url2):
        return urlparse(url1).hostname == urlparse(url2).hostname

    def get_url_path(self, datatype, verb, urltype, params={}, api_version=None):
        api_version = api_version or self.api_version
        templates = self._get_url_templates(api_version)

        url = templates[datatype][verb][urltype]
        return url.format(**params)

    def reverse_url(
        self,
        datatype,
        url,
        verb="GET",
        urltype="single",
        api_version=None,
        url_version=None,
    ):
        """
        Extracts parameters from a populated URL

        :param datatype: a string identifying the data the url accesses.
        :param url: the fully-qualified URL to extract parameters from.
        :param verb: the HTTP verb needed for use with the url.
        :param urltype: an adjective used to the nature of the request.
        :return: dict
        """
        api_version = api_version or self.api_version
        templates = self._get_url_templates(api_version)
        url_version = url_version or self.url_version

        # this is fairly simplistic, if necessary we could use the parse lib
        template_url = r"https://(?P<api_host>.+)/services/api/(?P<url_version>.+)"
        template_url += re.sub(
            r"{([^}]+)}", r"(?P<\1>.+)", templates[datatype][verb][urltype]
        )
        # /foo/{foo_id}/bar/{id}/
        m = re.match(template_url, url or "")
        if not m:
            raise KeyError(
                "No reverse match from '%s' to %s.%s.%s"
                % (url, datatype, verb, urltype)
            )

        r = m.groupdict()
        del r["api_host"]
        if r.pop("url_version") != url_version:
            raise ValueError("URL version mismatch")
        return r

    def get_url(
        self,
        datatype,
        verb,
        urltype,
        params={},
        api_host=None,
        api_version=None,
        url_version=None,
    ):
        """Returns a fully formed url

        :param datatype: a string identifying the data the url will access.
        :param verb: the HTTP verb needed for use with the url.
        :param urltype: an adjective used to the nature of the request.
        :param params: substitution variables for the URL.
        :return: string
        :rtype: A fully formed url.
        """
        api_version = api_version or self.api_version
        api_host = api_host or self.host
        url_version = url_version or self.url_version

        subst = params.copy()
        subst["api_host"] = api_host
        subst["api_version"] = api_version
        subst["url_version"] = url_version

        url = "https://{api_host}/services/api/{url_version}"
        url += self.get_url_path(datatype, verb, urltype, params, api_version)
        return url.format(**subst)

    def _get_url_templates(self, api_version):
        try:
            url_templates = self._URL_TEMPLATES[api_version]
        except KeyError:
            valid_api_vers = ", ".join(
                ["'{vers}'".format(vers=vers) for vers in self._URL_TEMPLATES.keys()]
            )
            raise ValueError(
                (
                    "'{api_version}' is not a valid `api_version`. "
                    "Currently supported API versions are: {valid_api_vers}."
                ).format(valid_api_vers=valid_api_vers, api_version=api_version)
            )
        return url_templates

    _URL_TEMPLATES = {
        "v1": {
            "LAYER": {
                "GET": {
                    "single": "/layers/{id}/",
                    "multi": "/layers/",
                    "multidraft": "/layers/drafts/",
                },
                "POST": {
                    "create": "/layers/",
                    "update": "/layers/{layer_id}/versions/import/",
                },
                "DELETE": {
                    "delete": "/layers/{id}/",
                },
            },
            "LAYER_VERSION": {
                "GET": {
                    "single": "/layers/{layer_id}/versions/{version_id}/",
                    "multi": "/layers/{layer_id}/versions/",
                    "draft": "/layers/{layer_id}/versions/draft/",
                    "published": "/layers/{layer_id}/versions/published/",
                },
                "POST": {
                    "create": "/layers/{layer_id}/versions/",
                    "import": "/layers/{layer_id}/versions/{version_id}/import/",
                    "publish": "/layers/{layer_id}/versions/{version_id}/publish/",
                },
                "PUT": {
                    "edit": "/layers/{layer_id}/versions/{version_id}/",
                },
                "DELETE": {
                    "single": "/layers/{layer_id}/versions/{version_id}/",
                },
            },
            "SET": {
                "GET": {
                    "single": "/sets/{id}/",
                    "metadata": "/sets/{id}/metadata/",
                    "multi": "/sets/",
                    "multidraft": "/sets/drafts/",
                },
                "POST": {
                    "create": "/sets/",
                },
                "DELETE": {
                    "delete": "/sets/{id}/",
                },
            },
            "SET_VERSION": {
                "GET": {
                    "single": "/sets/{id}/versions/{version_id}/",
                    "multi": "/sets/{id}/versions/",
                    "draft": "/sets/{id}/versions/draft/",
                    "published": "/sets/{id}/versions/published/",
                },
                "POST": {
                    "create": "/sets/{id}/versions/",
                    "publish": "/sets/{id}/versions/{version_id}/publish/",
                },
                "PUT": {
                    "edit": "/sets/{id}/versions/{version_id}/",
                },
                "DELETE": {
                    "single": "/sets/{id}/versions/{version_id}/",
                },
            },
            "CATALOG": {
                "GET": {
                    "multi": "/data/",
                    "latest": "/data/latest/",
                },
            },
            "PUBLISH": {
                "GET": {
                    "single": "/publish/{id}/",
                    "multi": "/publish/",
                },
                "POST": {
                    "create": "/publish/",
                },
                "DELETE": {
                    "single": "/publish/{id}/",
                },
            },
            "LICENSE": {
                "GET": {
                    "single": "/licenses/{id}/",
                    "multi": "/licenses/",
                    "cc": "/licenses/{slug}/{jurisdiction}/",
                },
            },
            "METADATA": {
                # InnerManager, so relative to a parent object
                "GET": {
                    "get": "metadata/",
                },
                "POST": {
                    "set": "metadata/",
                },
            },
            "SOURCE": {
                "GET": {
                    "single": "/sources/{id}/",
                    "multi": "/sources/",
                },
                "POST": {
                    "create": "/sources/",
                },
                "DELETE": {
                    "single": "/sources/{id}/",
                },
            },
            "SCAN": {
                "GET": {
                    "single": "/sources/{source_id}/scans/{scan_id}/",
                    "multi": "/sources/{source_id}/scans/",
                    "log": "/sources/{source_id}/scans/{scan_id}/log/",
                    "all": "/sources/scans/",
                },
                "DELETE": {
                    "cancel": "/sources/{source_id}/scans/{scan_id}/",
                },
                "POST": {
                    "create": "/sources/{source_id}/scans/",
                },
            },
            "DATASOURCE": {
                "GET": {
                    "multi": "/sources/{source_id}/datasources/",
                    "single": "/sources/{source_id}/datasources/{datasource_id}/",
                }
            },
            # InnerManager, so relative to a parent object
            "PERMISSION": {
                "GET": {
                    "multi": "permissions/",
                    "single": "permissions/{permission_id}/",
                },
                "POST": {
                    "single": "permissions/",
                },
                "PUT": {
                    "multi": "permissions/",
                },
            },
            "EXPORT": {
                "GET": {
                    "multi": "/exports/",
                    "single": "/exports/{id}/",
                },
                "POST": {
                    "create": "/exports/",
                    "validate": "/exports/validate/",
                },
                "OPTIONS": {
                    "options": "/exports/",
                },
                "DELETE": {
                    "single": "/exports/{id}/",
                },
            },
            "CROPLAYER": {
                "GET": {
                    "multi": "/exports/croplayers/",
                    "single": "/exports/croplayers/{id}/",
                },
            },
            "CROPFEATURE": {
                "GET": {
                    "multi": "/exports/croplayers/{croplayer_id}/cropfeatures/",
                    "single": "/exports/croplayers/{croplayer_id}/cropfeatures/{cropfeature_id}/",
                },
            },
        }
    }
