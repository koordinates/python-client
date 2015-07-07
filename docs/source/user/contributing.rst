Contributing
============

Koordinates welcomes bug reports and contributions by the community to this module. This process is intended to be as easy as possible for both contributors and the Koordinates development team.

Testing
-------

The client includes a suite of unit and functional tests. These should be used to verify that your changes don't break existing functionality, and that compatibility is maintained across supported Python versions. `Tests run automatically on CircleCI <https://circleci.com/gh/koordinates/python-client>`_ for branch commits and pull requests.

To run the tests you need to::

    $ pip install -r requirements.txt
    $ tox

Patches
-------

All patches should be sent as a pull request on GitHub, including tests and documentation where needed. If you’re fixing a bug or making a large change the patch *must* include test coverage before it will be merged.

If you're uncertain about how to write tests, take a look at some existing tests that are similar to the code you’re changing.


Release Process
---------------

This guide describes the process to release a new version of the library. In this example, ``v0.0.0``. The library follows the `Semantic Versioning guidelines <http://semver.org/>`_, so select major, minor, and patch version numbers appropriately.

Preparations
~~~~~~~~~~~~

#. Close or update all tickets for the `next milestone on Github.
   <https://github.com/koordinates/python-client/milestones?direction=asc&sort=due_date&state=open>`_.

#. Update the *minimum* required versions of dependencies in :file:`setup.py`.
   Update the *exact* version of all entries in :file:`requirements.txt`.

#. Run :command:`tox` from the project root. All tests for all supported Python versions must pass:

   .. code-block:: bash

    $ tox
    [...]
    ________ summary ________
    py27: commands succeeded
    py34: commands succeeded
    congratulations :)

   .. note::

    Tox will use the :file:`requirements.txt` to setup the virtualenvs, so make sure
    you've updated it!

#. Build the Sphinx docs. Make sure there are no errors and undefined references.

   .. code-block:: bash

    $ make clean docs

#. Check the `CircleCI build <https://circleci.com/gh/koordinates/python-client>`_ is passing.

#. Update the version number in :file:`koordinates/__init__.py` and commit:

   .. code-block:: bash

    $ git commit -m 'Bump version to 0.0.0' koordinates/__init__.py

   .. warning::

      Don't tag and push the changes yet so that you can safely rollback
      if you need change something!

#. Create a `draft release in Github <https://github.com/koordinates/python-client/releases/new>`_
   with a list of changes, acknowledgements, etc. 


Build and release
~~~~~~~~~~~~~~~~~

#. Test the release process. Build a source distribution and test it:

   .. code-block:: bash

    $ python setup.py sdist
    $ ls dist/
    koordinates-0.0.0.tar.gz

   Try installing them:

   .. code-block:: bash

    $ rm -rf /tmp/koordinates-sdist  # ensure clean state if ran repeatedly
    $ virtualenv /tmp/koordinates-sdist
    $ /tmp/koordinates-sdist/bin/pip install dist/koordinates-0.0.0.tar.gz
    $ /tmp/koordinates-sdist/bin/python
    >>> import koordinates
    >>> koordinates.__version__
    '0.0.0'

#. Create or check your accounts for the `test server <https://testpypi.python.org/pypi>`
   and `PyPI <https://pypi.python.org/pypi>`_. Update your :file:`~/.pypirc` with your
   credentials:

   .. code-block:: ini

    [distutils]
    index-servers =
        pypi
        test

    [test]
    repository = https://testpypi.python.org/pypi
    username = <test username>
    password = <test password>

    [pypi]
    repository = http://pypi.python.org/pypi
    username = <production username>
    password = <production password>

#. Upload the distributions for the new version to the test server and test the
   installation again:

   .. code-block:: bash

    $ python setup.py register -r test
    $ python setup.py sdist upload -r test
    $ pip install -i https://testpypi.python.org/pypi koordinates

#. Check if the package is displayed correctly:
   https://testpypi.python.org/pypi/koordinates

#. Upload the package to PyPI and test its installation one last time:

   .. code-block:: bash

    $ python setup.py register -r pypi
    $ python setup.py sdist upload -r pypi
    $ pip install -U koordinates

#. Check the package is displayed correctly:
   https://pypi.python.org/pypi/koordinates


Post release
~~~~~~~~~~~~

#. Push your changes:

   .. code-block:: bash

    $ git tag -a v0.0.0 -m "Version 0.0.0"
    $ git push origin v0.0.0

#. Activate the `documentation build
   <https://readthedocs.org/dashboard/koordinates-python/versions/>`_ for the new version.

#. Make the `Github release <https://github.com/koordinates/python-client/releases>`_ public.

#. Update related Zendesk pages if necessary.
