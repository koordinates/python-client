.. _install:

Installation
============

This part of the documentation covers the installation of the Koordinates Python Client Library.

Pip
---

Installing the Koordinates API Library is simple with `pip <https://pip.pypa.io>`_. All you need to do isrun the following in your terminal::

    $ pip install koordinates


Getting the Code
----------------

Koordinates API Library is `on GitHub <https://github.com/koordinates/python-client>`_.

Development occurs in the `master branch <https://github.com/koordinates/python-client/tree/master>`_, and releases are tagged and pushed to PyPI regularly.

You can either clone the public git repository::

    $ git clone git://github.com/koordinates/python-client.git

Or, download the `latest release <https://github.com/koordinates/python-client/releases/latest>`_.

Once you have a copy of the source, you can embed it in your Python package, or install it into your virtualenv/site-packages::

    $ python setup.py install


Upgrading
---------

We strongly encourage you to use the latest release of the API to ensure you get the benefit of fixes, improvements, and new features. The library follows the `Semantic Versioning guidelines <http://semver.org/>`_, so all releases with the same major version number (eg. ``1.x.x``) will be backwards compatible.
