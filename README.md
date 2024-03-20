# Koordinates Python API Client

A BSD-licensed Python client library for a number of [Koordinates](https://koordinates.com) web APIs.

The library provides easy access to Koordinates web services, particularly the [Publisher Admin APIs](https://help.koordinates.com/api/publisher-admin-api/).

[![Build status](https://badge.buildkite.com/5ce9ace71272791038722b9443fd4bb23620aec8041c10ea46.svg?branch=master)](https://buildkite.com/koordinates/python-client)

## Installation

To install the latest stable release of the library, simply:

```
pip install -U koordinates
```

The library is compatible with Python 3.7+.


## Documentation

* [Documentation for the Python library](http://koordinates-python.readthedocs.org)
* [Documentation on the APIs and available actions](https://help.koordinates.com/api/publisher-admin-api/)


## Support & Contributions

Please report bugs as [Github issues](https://github.com/koordinates/python-client/issues). For general technical support for the APIs and libraries, please contact us via [support.koordinates.com](https://support.koordinates.com).

We welcome contributions as pull requests - please open a new issue to start a discussion around a feature idea or bug. See the [Contributing notes](http://koordinates-python.readthedocs.org/en/latest/user/contributing.html) for more details.

## Code formatting

We use [Black](https://github.com/psf/black) to ensure consistent code formatting. We recommend integrating black with your editor:

* Sublime Text: install [sublack](https://packagecontrol.io/packages/sublack) via Package Control
* VSCode [instructions](https://code.visualstudio.com/docs/python/editing#_formatting)

We use the default settings.

One easy solution is to install [pre-commit](https://pre-commit.com), run `pre-commit install --install-hooks` and it'll automatically validate your changes code as a git pre-commit hook.
