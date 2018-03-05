#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
from codecs import open


version = ''
with open('koordinates/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='koordinates',
    packages=['koordinates',],
    version=version,
    description='A Python client library for a number of Koordinates web APIs',
    long_description=readme,
    author='Koordinates Limited',
    author_email='support@koordinates.com',
    url='https://github.com/koordinates/python-client',
    keywords='koordinates api',
    license = 'BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    entry_points = {
        'console_scripts': [
            'koordinates-create-token = koordinates.tokens:console_create',
        ],
    },
    install_requires=[
        'python-dateutil>=2,<3',
        'pytz',
        'requests>=2.5,<3',
        'requests-toolbelt>=0.4,<1',
        'six>=1.10.0,<2',
    ],
    extras_require={
        ':python_version=="2.7"': [
            'contextlib2',
        ],
    },
    tests_require=[
        'pytest>=3.3',
        'responses>=0.3',
        'coverage>=3.7,<4',
    ],
    zip_safe=False,
)

