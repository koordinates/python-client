# -*- coding: utf-8 -*-

"""
koordinates.token
~~~~~~~~~~~~~~~~~

Support for creating and managing API tokens via the `Token API`__.

__ https://support.koordinates.com/hc/en-us/articles/204890044-Koordinates-Token-API

"""
from __future__ import absolute_import

import logging

from koordinates import base
from koordinates.utils import make_date


logger = logging.getLogger(__name__)


class TokenManager(base.Manager):
    URL_KEY = 'TOKEN'

    def create(self, token, email, password):
        target_url = self.connection.get_url('TOKEN', 'POST', 'create')
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

        r = self.connection._raw_request('POST', target_url, json=post_data, headers={'Content-type': 'application/json'})
        return Token().deserialize(r.json(), self)


class Token(base.Model):
    ''' An API Token '''
    class Meta:
        manager = TokenManager
        serialize_skip = ('key',)

    @property
    def scopes(self):
        """ Read/Write accessor for the :ref:`Token.scope` property as a list of scope strings. """
        return (self.scope or '').split()

    @scopes.setter
    def scopes(self, value):
        self.scope = ' '.join(value or [])

    def __str__(self):
        s = "%s (%s): %s" % (self.id, self.name, self.key_hint)
        return s


def console_create():
    """ Command line tool to create an API token """
    import argparse
    import getpass
    import re
    import sys
    import requests
    from six.moves import input
    from koordinates.connection import Connection

    parser = argparse.ArgumentParser(description="Command line tool to create a Koordinates API Token.")
    parser.add_argument('site', help="Domain (eg. labs.koordinates.com) for the Koordinates site.", metavar="DOMAIN")
    parser.add_argument('email', help="User account email address")
    parser.add_argument('name', help="Description/name for the key")
    parser.add_argument('--scopes', help="Scopes for the new API token", nargs='+')
    parser.add_argument('--referrers', help="Restrict the request referrers for the token. You can use * as a wildcard, eg. *.example.com", nargs='+', metavar='HOST')
    parser.add_argument('--expires', help="Expiry time (ISO 8601 format)", metavar="TIMESTAMP")
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
    client = Connection(host=args.site, token='-dummy-')
    try:
        token = client.tokens.create(token, args.email, password)
    except requests.HTTPError as e:
        print("%s: %s" % (e, e.response.text))

        # Helpful tips for specific errors
        if e.response.status_code == 401:
            print("  => Check your email address, password, and site domain carefully.")

        sys.exit(1)

    print("Token created successfully.\n  Key: %s\n  Scopes: %s" % (token.key, token.scope))
