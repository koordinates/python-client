import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import requests
import uuid

import requests
import logging
from datetime import datetime

from koordinates import Connection
from koordinates import Token

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


def gettoken():
    if 'KOORDINATES_TOKEN' in os.environ:
        return os.environ['KOORDINATES_TOKEN']
    else:
        raise Exception('No authentication token specified, and KOORDINATES_TOKEN not available in the environment.')

def get_id(url):
    lst_path = os.path.split(url)
    if lst_path[1] == "":
        lst_path = os.path.split(lst_path[0])
    return lst_path[1]


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

def target_url(id=8093):
    url_templates = {}
    url_templates['GET'] = {}
    url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''
    return url_templates['GET']['single'].format(layer_id=id)
def sub_token_test():
    obj_conn_c = Connection(host='test.koordinates.com')
    idx = 0
    target_delete_id = None
    target_update_id = None
    tok_for_update = None
    for tok in obj_conn_c.tokens.list():
        print(tok.id, " " ,get_id(tok.url), " " , tok.name)
        if idx == 0:
            target_delete_id = get_id(tok.url)
        if idx == 2:
            tok_for_update = tok
            target_update_id = get_id(tok.url)
        idx += 1

    d=datetime.now()
    my_name = "Test Token - {}".format(d.strftime('%Y%m%dT%H%M%S'))
    obj_tok = Token(name=my_name)
    obj_tok.scope = "query tiles catalog wxs:wfs wxs:wms wxs:wcs tokens:write tokens:read "
    obj_tok.expires_at = '2015-08-01T08:00:00Z'
    obj_tok.referrers = None
    obj_tok_new = obj_conn_c.tokens.create(obj_tok, 'rshea@thecubagroup.com', 'mercatorproj1000')
    print("{} has key of {}".format(obj_tok_new.name, obj_tok_new.key))
    obj_tok_new.name = obj_tok_new.name + " A"
    print("{} has key of {}".format(obj_tok_new.name, obj_tok_new.key))
    obj_tok_new.save()

def main_token_test():
    username = input("What is your userid? ")
    pwd = getpass()

    if False:
        #Phase 1
        obj_conn_a = Connection(host='test.koordinates.com', token=gettoken())
        print("List existing tokens")
        for tok in obj_conn_a.tokens.list():
            print(get_id(tok.url), " " , tok.name)

    #Phase 2
    obj_conn_b = Connection(host='test.koordinates.com', token='-dummy-')
    d=datetime.now()
    my_name = "Test Token - {}".format(d.strftime('%Y%m%dT%H%M%S'))
    obj_tok = Token(name=my_name)
    obj_tok.scope = "query tiles catalog wxs:wfs wxs:wms wxs:wcs tokens:write tokens:read "
    obj_tok.expires_at = '2015-08-01T08:00:00Z'
    obj_tok.referrers = None
    print("1", "-" * 40)
    print("About to create new token named : {}".format(my_name))
    print("2", "-" * 40)
    obj_tok_new = obj_conn_b.tokens.create(obj_tok, 'rshea@thecubagroup.com', 'mercatorproj1000')
    print("Created token with key : {}".format(obj_tok_new.key))
    obj_conn_c = Connection(host='test.koordinates.com', token=obj_tok_new.key)
    print("List existing tokens including new one")
    idx = 0
    target_delete_id = None
    target_update_id = None
    tok_for_update = None
    for tok in obj_conn_c.tokens.list():
        print(tok.id, " " ,get_id(tok.url), " " , tok.name)
        if idx == 0:
            target_delete_id = get_id(tok.url)
        if idx == 2:
            tok_for_update = tok
            target_update_id = get_id(tok.url)
        idx += 1

    #Phase 3
    print("3", "-" * 40)
    print("About to delete a token with id : {}".format(target_delete_id))
    obj_conn_c.tokens.delete(target_delete_id)
    print("Deleted a token with id : {}".format(target_delete_id))
    #Phase 4
    import pdb;pdb.set_trace()
    print("4", "-" * 40)
    print("About to update a token with id : {}".format(target_update_id))
    tok_for_update.name = "{} {}".format(tok_for_update.name, "A")
    tok_for_update.save()
    print("Updated a token with id : {}".format(target_delete_id))



def main17(username):
    '''
    Fetch a single Layer object
    '''
    conn = Connection(host='test.koordinates.com')
    obj_layer = conn.layers.get(8093)
    print("")
    print(obj_layer.tags)
    print("")
    print(obj_layer.data.crs)
    print("")
    for f in obj_layer.data.fields:
        print(f['name'])
    print("")
    print(obj_layer.collected_at)
    print("")
    print(obj_layer.id, " ", obj_layer.title, " ", id(obj_layer), make_list_string(obj_layer.tags))
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
    url = target_url(id=8093)
    if False:
        main17(username)
    sub_token_test()

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
