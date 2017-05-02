#
layer_list_permissions_good_simulated_response = '''[{
        "permission": "download",
        "id": "group.everyone",
        "group": {
            "id": 4,
            "url": "https://test.koordinates.com/services/api/v1/groups/4/",
            "name": "Everyone",
            "country": null
        }
    }]'''

set_list_permissions_good_simulated_response = '''[{
        "permission": "admin",
        "id": "user.4",
        "user": {
            "id": 4,
            "first_name": "Admin",
            "last_name": "TestUser",
            "url": "https://test.koordinates.com/services/api/v1/users/4/",
            "country": "AF"
        }
    },
    {
        "permission": "admin",
        "id": "group.administrators",
        "group": {
            "id": 3,
            "url": "https://test.koordinates.com/services/api/v1/groups/3/",
            "name": "Site Administrators",
            "country": null
        }
    },
    {
        "permission": "view",
        "id": "group.everyone",
        "group": {
            "id": 1,
            "url": "https://test.koordinates.com/services/api/v1/groups/1/",
            "name": "Everyone",
            "country": null
        }
    }]'''

source_list_permissions_good_simulated_response = set_list_permissions_good_simulated_response

layer_permission_simulated_response = '''{
        "id": "group.108",
        "group": {
            "id": 108,
            "url": "https://test.koordinates.com/services/api/v1/groups/108/",
            "name": "Example Group",
            "country": "NZ"
        },
        "permission": "edit"
    }'''

set_permission_simulated_response = '''{
        "id": "group.34",
        "group": {
            "id": 34,
            "url": "https://test.koordinates.com/services/api/v1/groups/34/",
            "name": "Magic Group",
            "country": "AR"
        },
        "permission": "edit"
    }'''

source_permission_simulated_response = '''{
        "id": "group.85",
        "group": {
            "id": 85,
            "url": "https://test.koordinates.com/services/api/v1/groups/85/",
            "name": "aliBaba Group",
            "country": "FR"
        },
        "permission": "download"
    }'''

