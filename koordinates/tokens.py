# -*- coding: utf-8 -*-

"""
koordinates.token
=================

Support for creating and managing API tokens via the `Token API`__.

__ https://help.koordinates.com/api/publisher-admin-api/token-api/

"""
from __future__ import absolute_import

import logging

from koordinates import base
from koordinates.utils import make_date
from .utils import is_bound

logger = logging.getLogger(__name__)


class TokenManager(base.Manager):
    """
    Accessor for querying Tokens.

    Access via the ``tokens`` property of a :py:class:`koordinates.client.Client` instance.
    """


    _URL_KEY = 'TOKEN'

    def delete(self, id ):
        """ Delete a token """
        target_url = self.client.get_url('TOKEN', 'DELETE', 'single', {'id':id})

        r = self.client.request('DELETE', target_url, headers={'Content-type': 'application/json'})
        r.raise_for_status()


    def create(self, token, email, password):
        """
        Create a new token

        :param Token token: Token instance to create.
        :param str email: Email address of the Koordinates user account.
        :param str password: Koordinates user account password.
        """
        target_url = self.client.get_url('TOKEN', 'POST', 'create')
        post_data = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'name': token.name,
        }
        if getattr(token, 'scope', None):
            post_data['scope'] = token.scope
        if getattr(token, 'expires_at', None):
            post_data['expires_at'] = token.expires_at
        if getattr(token, 'referrers', None):
            post_data['referrers'] = token.referrers

        r = self.client._raw_request('POST', target_url, json=post_data, headers={'Content-type': 'application/json'})
        return self.create_from_result(r.json())


class Token(base.Model):
    '''
    Represents an API Token.
    '''
    class Meta:
        manager = TokenManager
        serialize_skip = ('key',)

    @property
    def scopes(self):
        """ Read/Write accessor for the :py:attr:`.scope` property as a list of scope strings. """
        return (self.scope or '').split()

    @scopes.setter
    def scopes(self, value):
        self.scope = ' '.join(value or [])

    def __str__(self):
        s = "%s (%s): %s" % (self.id, self.name, self.key_hint)
        return s

    @is_bound
    def save(self):
        """ Saves changes to a token """
        target_url = self._client.get_url('TOKEN', 'PUT', 'update', {'id': self.id})
        r = self._client.request('PUT', target_url, json=self._serialize())
        return self._deserialize(r.json(), self._manager)


def console_create():
    """
    Command line tool (``koordinates-create-token``) used to create an API token.
    """
    import argparse
    import getpass
    import re
    import sys
    import requests
    from six.moves import input
    from koordinates.client import Client

    parser = argparse.ArgumentParser(description="Command line tool to create a Koordinates API Token.")
    parser.add_argument('site', help="Domain (eg. labs.koordinates.com) for the Koordinates site.", metavar='SITE')
    parser.add_argument('email', help="User account email address", metavar='EMAIL')
    parser.add_argument('name', help="Description for the key", metavar='NAME')
    parser.add_argument('--scopes', help="Scopes for the new API token", nargs='+', metavar="SCOPE")
    parser.add_argument('--referrers', help="Restrict the request referrers for the token. You can use * as a wildcard, eg. *.example.com", nargs='+', metavar='HOST')
    parser.add_argument('--expires', help="Expiry time in ISO 8601 (YYYY-MM-DD) format", metavar="DATE")
    args = parser.parse_args()

    # check we have a valid-ish looking domain name
    if not re.match(r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)', args.site):
        parser.error("'%s' doesn't look like a valid domain name." % args.site)

    # check we have a valid-ish looking email address
    if not re.match(r'[^@]+@[^@]+\.[^@]+$', args.email):
        parser.error("'%s' doesn't look like a valid email address." % args.email)

    password = getpass.getpass('Account password for %s: ' % args.email)
    if not password:
        parser.error("Empty password.")

    expires_at = make_date(args.expires)

    print("\nNew API Token Parameters:")
    print("  Koordinates Site: %s" % args.site)
    print("  User email address: %s" % args.email)
    print("  Name: %s" % args.name)
    print("  Scopes: %s" % ' '.join(args.scopes or ['(default)']))
    print("  Referrer restrictions: %s" % ' '.join(args.referrers or ['(none)']))
    print("  Expires: %s" % (expires_at or '(never)'))
    if input("Continue? [Yn] ").lower() == 'n':
        sys.exit(1)

    token = Token(name=args.name)
    if args.scopes:
        token.scopes = args.scopes
    if args.referrers:
        token.referrers = args.referrers
    if expires_at:
        token.expires_at = expires_at

    print("\nRequesting token...")
    # need a dummy token here for initialisation
    client = Client(host=args.site, token='-dummy-')
    try:
        token = client.tokens.create(token, args.email, password)
    except requests.HTTPError as e:
        print("%s: %s" % (e, e.response.text))

        # Helpful tips for specific errors
        if e.response.status_code == 401:
            print("  => Check your email address, password, and site domain carefully.")

        sys.exit(1)

    print("Token created successfully.\n  Key: %s\n  Scopes: %s" % (token.key, token.scope))
