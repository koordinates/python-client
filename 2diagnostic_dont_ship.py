import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import requests
import uuid

import requests
import logging

import koordinates.api as api
from koordinates import Connection

#import koordinates.chainclasstest as chainclasstest

class TestClass(object):
    def __init__(self, v):
        self.value = v
    def makeme(self, v):
        self.the_list.append(str(uuid.uuid1()))
        return self.__class__(v)
class TestClassSub(TestClass):
    pass
class TestClassSubSub(TestClassSub):
    def __init__(self, v):
        self.value = v
        self.the_list = []


def getpass():
    '''
    Prompt user for Password until there is a Connection object
    '''
    import getpass

    if 'KPWD' in os.environ:
        return os.environ['KPWD']
    else:
        return(getpass.getpass('Please enter your Koordinates password: '))

def get_auth(u, p):
    """Creates an Authorisation object
    """
    return requests.auth.HTTPBasicAuth(u, p)

def make_list_string(lst):
    return "| ".join(lst)

def target_url(id=1474):
    url_templates = {}
    url_templates['GET'] = {}
    url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''
    return url_templates['GET']['single'].format(layer_id=id)
def main17(username):
    '''
    Fetch a single Layer object
    '''
    conn = Connection()
    conn.layer.get(1474)
    print("")
    print(conn.layer.tags)
    print("")
    print(conn.layer.data.crs)
    print("")
    for f in conn.layer.data.fields:
        print(f.name)
    print("")
    print(conn.layer.collected_at)
    print("")
    print(conn.layer.id, " ", conn.layer.name, " ", id(conn.layer), make_list_string(conn.layer.tags))
    print("")

def logger_tester(log):
    '''
    To test the koordinates logger
    '''
    if log:
        import logging
        logger = logging.getLogger(__name__)
        logging.basicConfig(filename='example.log',level=logging.DEBUG)
        logging.debug('This message should go to the log file')
        logging.info('So should this')
        logging.warning('And this, too')

def main(cmdargs):
    do_some_logging=True
    username = 'rshea@thecubagroup.com'
    url = target_url(id=1474)
    main17(username)

def getcommandlineargs():
    '''
    Read command line args to get input and output paths
    '''
    print("If args are supplied the first is the layerid to be published, the second is the corresponding versionid")
    dout = {'layerid': -1, 'versionid': -1}
    if len(sys.argv) < 3:
        print("No publishing information provided")
    else:
        dout['layerid'] = int(sys.argv[1])
        dout['versionid'] = int(sys.argv[2])

    return dout


if __name__ == "__main__":
    cmdargs = getcommandlineargs()
    main(cmdargs)
