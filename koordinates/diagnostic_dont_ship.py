import requests
import sys
import os

import api
import koordexceptions
import chainclasstest

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

def target_url(id=1474):
    url_templates = {}
    url_templates['GET'] = {}
    url_templates['GET']['single'] = '''https://koordinates.com/services/api/v1/layers/{layer_id}/'''
    return url_templates['GET']['single'].format(layer_id=id) 

def main4(username):
    #conn = api.Connection(username, getpass())
    conn = api.Connection(username, getpass(), 'data.linz.govt.nz')
    #for x in conn.layer.get_list().filter('Line of lowest astronomical tide for Australia').order_by('name').execute_get_list():
    # conn.layer.get_list().filter('Quattroshapes').order_by('name').execute_get_list():
    for x in conn.layer.get_list().filter('Quattroshapes').order_by('name').execute_get_list():
        print(x.id, " ", x.name, " ", id(x))
    # conn.layer.get_list().filter('Finland').order_by('name').execute_get_list()

def main3():
    #cctold = chainclasstest.ChainClassTestOld([1,20,3,40])
    #print(cctold.order_by().filter_by())
    #print(cctold.filter_by().order_by())
    print()
    cct = chainclasstest.ChainClassTest([1,20,3,40], 
                                        -999,
                                        '''https://koordinates.com/services/api/v1/layers/''')
    print("0" * 50)
    print(cct.url)
    print("1" * 50)
    cct.outputparsedurl()
    print("2" * 50)
    #cct.filter_by(name__contains='Wellington')
    print("3" * 50)
    #cct.filter_by(name__contains='Wellington').order_by()
    print("4" * 50)
    #cct.order_by().filter_by(name__contains='Wellington')
    cct.get_list().filter_by(name__contains='Wellington').order_by()
    print("5" * 50)
    cct.outputparsedurl()
    print("6" * 50)
    print(cct.url)
    print("7" * 50)
    '''
    print(cct)
    print(cct.order_by())
    print(cct.filter_by())
    '''
    '''
    print(cct.order_by().filter_by())
    '''
#def main2(username, url):
#    conn = api.Connection(username, getpass())
#    conn.layer.get(9999)
def main1(username, url):
    the_auth=get_auth(username, getpass())
    my_config = {'verbose': sys.stderr}
    import requests
    import logging

    #print(dir())
    #conn = api.Connection(username, getpass())
    #conn.layer.get(1474)


    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig() 
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    #
    req_resp = requests.get(url, auth=the_auth)
    #
    print("")
    print (type(req_resp.status_code))
    print("")
    if req_resp.status_code == "200":
        print("valid")
    else:
        print("invalid")
    print("")
    if req_resp.status_code == 200:
        print("valid")
    else:
        print("invalid")
    #
    #
    #
    
    print(dir())
def main():
    username = 'rshea@thecubagroup.com'
    url = target_url(id=1474)
    if False:
        main1(username, url)
    #main2(username, url)
    #main3()
    main4(username)

if __name__ == "__main__":
    main()
