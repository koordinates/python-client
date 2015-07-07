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
