#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='koordinates',
    packages=['koordinates',],
    version='0.1.0',
    description='koordinates is a Python client library for a number of Koordinates web APIs',
    author='Richard Shea',
    author_email='rshea@thecubagroup.com',
    url='https://github.com/koordinates/python-client',
    download_url = 'https://github.com/koordinates/python-client/tarball/0.1', 
    keywords='koordinates api',
    license = 'BSD',
    classifiers=[],
    test_suite='tests',
)
