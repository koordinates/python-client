# -*- coding: utf-8 -*-
'''
Koordinates API Library

:copyright: (c) 2015 by Koordinates .
:license: BSD, see LICENSE for more details.

'''

__title__ = 'koordinates'
__version__ = '0.3.0'
__author__ = 'Richard Shea'
__license__ = 'BSD'
__copyright__ = 'Copyright 2015 Koordinates'


import logging
try: 
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
