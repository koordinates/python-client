import json
from collections import namedtuple, Iterable

MYJSON = '''{
    "name": "Fred",
    "age": 99,
    "heightcms": 180
}'''
MYOTHERJSON = '''
{
    "name": "Fred",
    "age": 99,
    "co
    "heightcms": 180,
    "vehicles": {
        "totalcost": 95000,
        "car": {
            "colour": "white",
            "year": 2010
        },
        "boat": {
            "name": "Lucy Lu",
            "lengthmetres": 4.5
        }
    }
}
'''
MYOTHERJSON2 ='''
{
    "name": "Fred",
    "age": 99,
    "heightcms": 180,
    "countries_visited": [
        "France",
        "Germany",
        "Italy"
    ],
    "children": [
        {"age":10, "name":"Freda"},
        {"age":12, "name":"Andrew"},
        {"age":14, "name":"Mary"}
    ],
    "vehicles": {
        "totalcost": 95000,
        "car": {
            "colour": "white",
            "year": 2010,
            "addons": [
                "Radio",
                "Air-Con",
                "FogLamps"
            ]
        },
        "boat": {
            "name": "Lucy Lu",
            "lengthmetres": 4.5
        }
    }
}
'''
MYOTHERJSON3 ='''
{
    "name": "Fred",
    "age": 99,
    "heightcms": 180,
    "countries_visited": [
        "France",
        "Germany",
        "Italy"
    ],
    "vehicles": {
        "totalcost": 95000,
        "car": {
            "colour": "white",
            "year": 2010,
            "addons": [
                "Radio",
                "Air-Con",
                "FogLamps"
            ]
        },
        "boat": {
            "name": "Lucy Lu",
            "lengthmetres": 4.5
        }
    }
}
'''
from tests.canned_responses_for_tests_2 import layers_single_good_simulated_response
class InnerJsonTester(object):
    def __init__(self, s):
        self.innertest = s 


class JsonTester(object):
    def __class_builder(self, the_dic, the_name):
            dic_out = {}
            bln_has_nested_dic = False
            for k, v in the_dic.items():
                if isinstance(v, dict):
                    dic_out[k] = self.__class_builder(v, k) 
                else:
                    dic_out[k] = v 
            return type(the_name.title(), (object,), dic_out)



    def __init__(self, my_json):
        #self.innertest = InnerJsonTester("inner test")
        #self.test = "test"
        o = json.loads(my_json)
        print(type(o))
        for k, v in o.items():
#            if isinstance(v, dict) or isinstance(v, list) or isinstance(v, tuple):
#                #tricky stuff - possibly recurse ?
#                if isinstance(v, dict):
#                    print("Need to make this into a Class/Obj : {}".format(k))
#                    my_att = self.__class_builder(o[k], k)
#                else:
#                    my_att = getattr(o[k], k, "")
#                    print(my_att)
#                    setattr(self, k, o[k])
#            else:
#                my_att = getattr(o[k], k, "")
#                print(my_att)
#                setattr(self, k, o[k])
            if isinstance(v, dict):
                print("Need to make this into a Class/Obj : {}".format(k))
                att_value = self.__class_builder(o[k], k)
            elif isinstance(v, list) or isinstance(v, tuple):
                cnt_dicts_present = 0
                for element in v:
                    if isinstance(element, dict):
                        cnt_dicts_present += 1
                if cnt_dicts_present > 0:
                    raise NotImplementedError("Associative Array found within Sequence in data returned from server. This is not yet supported") 
                else:
                    att_value = v 
            else:
                att_value = v 
            print(att_value)
            setattr(self, k, att_value)

        #set_namedtuple = json.loads(my_json, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
#        for k in set_namedtuple.__dict__.keys():
#            my_att = getattr(set_namedtuple, k, "")
#            setattr(self, k, my_att)

def analyse_object_attributes(obj):
    for attribute in [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]:
        print(attribute, " " , type(attribute))
    print(obj)
    print(obj.__dict__)
    print(type(obj))


def main():
    #jt = JsonTester(layers_single_good_simulated_response)
    jt = JsonTester(MYOTHERJSON3)
    print("A")
    print(jt)
    print("B")
    print(jt.__dict__)
    print("C")
    print(jt.name)
    print(jt.vehicles)
    print(jt.vehicles.totalcost)
    print(jt.vehicles.car.colour)
    print(jt.vehicles.car.addons)
    print(jt.vehicles.boat.name)
    print(jt.age)
    #analyse_object_attributes(jt)


if __name__ == "__main__":
    main()

