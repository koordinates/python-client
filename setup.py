#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='koordinates-api-client',
    packages=['koordinates_api_client',],
    version='0.1.0',
    description='koordinates-api-client exists only to test uploading to pypi',
    author='Richard Shea',
    author_email='rshea@thecubagroup.com',
    url='https://github.com/koordinates/python-client',
    download_url = 'https://github.com/koordinates/python-client/tarball/0.1', 
    keywords='koordinates api',
    license = 'Apache License 2.0',
    classifiers=[],
)
