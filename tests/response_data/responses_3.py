sets_single_good_simulated_response = """{
  "id": 933,
  "title": "Ultra Fast Broadband Initiative Coverage",
  "description": "",
  "description_html": "",
  "categories": [],
  "tags": [],
  "group": {
    "id": 141,
    "url": "https://test.koordinates.com/services/api/v1/groups/141/",
    "name": "New Zealand Broadband Map",
    "country": "NZ"
  },
  "items": [
    "https://test.koordinates.com/services/api/v1/layers/4226/",
    "https://test.koordinates.com/services/api/v1/layers/4228/",
    "https://test.koordinates.com/services/api/v1/layers/4227/",
    "https://test.koordinates.com/services/api/v1/layers/4061/",
    "https://test.koordinates.com/services/api/v1/layers/4147/",
    "https://test.koordinates.com/services/api/v1/layers/4148/"
  ],
  "url": "https://test.koordinates.com/services/api/v1/sets/933/",
  "url_html": "https://test.koordinates.com/set/933-ultra-fast-broadband-initiative-coverage/",
  "metadata": null,
  "created_at": "2012-03-21T21:49:51.420Z"
}"""


sets_new_draft_good_simulated_response = """{
  "id": 1,
  "title": "New Set",
  "url": "https://test.koordinates.com/services/api/v1.x/sets/1/",
  "type": "set",
  "created_at": "2020-05-12T03:25:57.717683Z",
  "thumbnail_url": "https://tiles-test.koordinates.com/services/tiles/v4/thumbnail/set=4.4,style=auto/1200x630.png",
  "description": "Test New Set",
  "description_html": "<p>Test New Set</p>",
  "latest_version": "https://test.koordinates.com/services/api/v1.x/sets/1/versions/1/",
  "published_version": null,
  "this_version": "https://test.koordinates.com/services/api/v1.x/sets/1/versions/1/",
  "publisher": "https://test.koordinates.com/services/api/v1.x/publishers/test.koordinates.com:108/",
  "categories": [],
  "tags": [],
  "group": {
    "id": 141,
    "url": "https://test.koordinates.com/services/api/v1/groups/141/",
    "name": "New Zealand Broadband Map",
    "country": "NZ"
  },
  "url_html": "https://test.koordinates.com/set/1/",
  "metadata": null,
  "publish_to_catalog_services": false,
  "active_publish": null,
  "permissions": "https://test.koordinates.com/services/api/v1.x/sets/1/permissions/",
  "settings": {
      "lock_title_to_metadata": false,
      "lock_description_to_metadata": false,
      "lock_tags_to_metadata": false
  },
  "items": [
      "https://test.koordinates.com/services/api/v1.x/layers/2/",
      "https://test.koordinates.com/services/api/v1.x/layers/1/"
  ],
  "version": {
      "id": 1,
      "url": "https://test.koordinates.com/services/api/v1.x/sets/1/versions/1/",
      "created_at": "2020-05-12T03:25:57.848738Z"
  }
}"""

sets_single_draft_good_simulated_response = """[{
    "id": 1,
    "title": "New Set",
    "url": "https://test.koordinates.com/services/api/v1.x/sets/1/",
    "type": "set",
    "created_at": "2020-05-11T03:51:38.847490Z",
    "thumbnail_url": "https://tiles-test.koordinates.com/services/tiles/v4/thumbnail/set=2.2,style=auto/1200x630.png"
  }]"""


sets_multi_version_good_simulated_response = """[{
  "id": 1,
  "url": "https://test.koordinates.com/services/api/v1.x/sets/1/versions/1/",
  "created_at": "2012-12-19T23:13:26.324088Z"
},
{
  "id": 5,
  "url": "https://test.koordinates.com/services/api/v1.x/sets/1/versions/5/",
  "created_at": "2020-05-13T03:05:23.145705Z"
}]"""

sets_single_version_good_simulated_response = """{
  "id": 5,
  "title": "New Set Test",
  "url": "https://test.koordinates.com/services/api/v1.x/sets/5/",
  "type": "set",
  "created_at": "2020-05-14T01:06:48.048303Z",
  "thumbnail_url": "https://tiles-test.koordinates.com/services/tiles/v4/thumbnail/set=5.10,style=auto/1200x630.png",
  "description": "Testing Sets",
  "description_html": "<p>Testing Sets</p>",
  "latest_version": "https://test.koordinates.com/services/api/v1.x/sets/5/versions/10/",
  "published_version": "https://test.koordinates.com/services/api/v1.x/sets/5/versions/10/",
  "this_version": "https://test.koordinates.com/services/api/v1.x/sets/5/versions/10/",
  "publisher": "https://test.koordinates.com/services/api/v1.x/publishers/test.koordinates.com:108/",
  "categories": [],
  "tags": [],
  "group": {
      "id": 108,
      "url": "https://test.koordinates.com/services/api/v1.x/groups/108/",
      "name": "Group Mapstream",
      "country": "NZ"
  },
  "url_html": "https://test.koordinates.com/set/5-new-set-test/",
  "metadata": null,
  "publish_to_catalog_services": false,
  "active_publish": null,
  "items": [
      "https://test.koordinates.com/services/api/v1.x/layers/1/"
  ],
  "version": {
      "id": 10,
      "url": "https://test.koordinates.com/services/api/v1.x/sets/5/versions/10/",
      "created_at": "2020-05-14T03:20:59.739650Z"
  }
}"""

sets_publish_version_good_simulated_response = """{
  "id": 10,
  "url": "https://test.koordinates.com/services/api/v1/publish/10/",
  "state": "publishing",
  "created_at": "2015-06-08T10:39:44.823Z",
  "created_by": {
    "id": 108,
    "url": "https://test.koordinates.com/services/api/v1.x/groups/108/",
    "name": "Group Mapstream",
    "country": "NZ"
  },
  "error_strategy": "abort",
  "publish_strategy": "together",
  "publish_at": null,
  "items": [
      "https://test.koordinates.com/services/api/v1.x/layers/1/"
  ]
}"""
