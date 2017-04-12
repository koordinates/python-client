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

table_list_permissions_good_simulated_response = '''[{
        "permission": "download",
        "id": "group.everyone",
        "group": {
            "id": 1,
            "url": "https://test.koordinates.com/services/api/v1/groups/1/",
            "name": "Everyone",
            "country": null
        }
    }]'''

document_list_permissions_good_simulated_response = '''[{
        "permission": "view",
        "id": "group.everyone",
        "group": {
            "id": 1,
            "url": "https://test.koordinates.com/services/api/v1/groups/1/",
            "name": "Everyone",
            "country": null
        }
    }]'''

source_list_permissions_good_simulated_response = '''[{
        "permission": "admin",
        "id": "group.administrators",
        "group": {
            "id": 3,
            "url": "https://test.koordinates.com/services/api/v1/groups/3/",
            "name": "Site Administrators",
            "country": null
        }
    }]'''

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

table_permission_simulated_response = '''{
        "id": "group.123",
        "group": {
            "id": 123,
            "url": "https://test.koordinates.com/services/api/v1/groups/123/",
            "name": "Edit Group",
            "country": "ES"
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
        "id": "group.67",
        "group": {
            "id": 67,
            "url": "https://test.koordinates.com/services/api/v1/groups/67/",
            "name": "Exclusive Group",
            "country": "AR"
        },
        "permission": "view"
    }'''

document_permission_simulated_response = '''{
        "id": "group.22",
        "group": {
            "id": 22,
            "url": "https://test.koordinates.com/services/api/v1/groups/22/",
            "name": "Download Group",
            "country": "AR"
        },
        "permission": "download"
    }'''
