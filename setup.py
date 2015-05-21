#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
import os
from codecs import open


version = ''
with open('koordinates/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

history = ''

setup(
    name='koordinates',
    packages=['koordinates',],
    version=version,
    description='koordinates is a Python client library for a number of Koordinates web APIs',
    long_description=readme + '\n\n' + history, 
    author='Richard Shea',
    author_email='rshea@thecubagroup.com',
    url='https://github.com/koordinates/python-client',
    download_url = 'https://github.com/koordinates/python-client/tarball/0.1', 
    keywords='koordinates api',
    license = 'BSD',
    classifiers=[],
    test_suite='koordinates.tests',
)

