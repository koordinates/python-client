#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

package_pwd = None

def getpass():
    '''
    Prompt user for Password until there is a Connection object
    '''
    import getpass
    if ('CIRCLECI' in os.environ) and ('KPWD' in os.environ):
        #circleci specific
        return os.environ['KPWD']
    elif ('KPWDDEV' in os.environ):
        #localdev environment
        return os.environ['KPWDDEV']
    else:
        return(getpass.getpass('Please enter your Koordinates password: '))

def setup_package():
    global package_pwd
    package_pwd = getpass()

def teardown_package():
    pass
