#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_exports
----------------------------------

Tests for the `koordinates.exports` module.
"""


import io
import os
import shutil
import tempfile

import pytest
import responses

# from koordinates import api
from koordinates import exceptions
from koordinates import Client, Export, Layer, DownloadError
from koordinates.exports import ExportValidationResponse, CropLayer, CropFeature

from .response_data.exports import (
    creation_ok,
    validation_ok,
    validation_error,
    cancel_ok,
    cancel_error,
    croplayer_list,
    cropfeature_list,
    croplayer_detail,
    cropfeature_detail,
    export_list,
    export_detail,
    export_complete,
    export_format_options,
)


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


@responses.activate
def test_export_list(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "multi"),
        body=export_list,
        status=200,
        content_type="application/json",
    )

    export_count = 0
    for e in client.exports.list():
        export_count += 1
        if e == 0:
            assert e.id == 19
            assert e.name == "kx-new-zealand-2layers-JPEG-SHP"
            assert e.created_at.isoformat() == "2016-04-20T22:31:19.242850+00:00"
            assert e.created_via == "web"
            assert e.state == "complete"
            assert e.url == "https://test.koordinates.com/services/api/v1/exports/19/"
            assert (
                e.download_url
                == "https://test.koordinates.com/services/api/v1/exports/19/download/"
            )

    assert export_count == 5


@responses.activate
def test_export_detail(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_complete,
        status=303,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.id == 19
    assert e.name == "kx-new-zealand-2layers-JPEG-SHP"
    assert e.created_at.isoformat() == "2016-04-20T22:31:19.242850+00:00"
    assert e.created_via == "web"
    assert e.state == "complete"
    assert e.url == "https://test.koordinates.com/services/api/v1/exports/19/"
    assert (
        e.download_url
        == "https://test.koordinates.com/services/api/v1/exports/19/download/"
    )
    assert e.extent == None
    assert e.delivery == {"method": "download"}
    assert e.formats == {"raster": "image/jpeg", "vector": "application/x-zipped-shp"}
    assert len(e.items) == 2
    assert e.options == {}
    assert e.crs == "EPSG:2193"
    assert e.size_estimate_zipped == 1905906
    assert e.progress == 1.0


@responses.activate
def test_export_download(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_complete,
        status=200,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.state == "complete"
    assert (
        e.download_url
        == "https://test.koordinates.com/services/api/v1/exports/19/download/"
    )

    responses.add(
        responses.GET,
        e.download_url,
        body="some data",
        status=200,
        content_type="application/zip",
        adding_headers={
            "Content-Length": "9",
            "Content-Disposition": "attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip",
        },
    )

    td = tempfile.mkdtemp()
    try:
        filename = e.download(td)
        assert filename == "kx-new-zealand-2layers-JPEG-SHP.zip"
    finally:
        shutil.rmtree(td)


@responses.activate
def test_export_download_unavailable(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_detail,
        status=200,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.state == "processing"
    assert e.download_url == None

    pytest.raises(DownloadError, e.download, tempfile.tempdir)


@responses.activate
def test_export_download_filename(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_complete,
        status=200,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.state == "complete"
    assert (
        e.download_url
        == "https://test.koordinates.com/services/api/v1/exports/19/download/"
    )

    responses.add(
        responses.GET,
        e.download_url,
        body="some data",
        status=200,
        content_type="application/zip",
        adding_headers={
            "Content-Length": "9",
            "Content-Disposition": "attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip",
        },
    )

    td = tempfile.mkdtemp()
    try:
        tf = os.path.join(td, "filey.mcfileface")
        filename = e.download(tf)
        assert os.path.isfile(tf)
        assert os.path.getsize(tf) == 9
        assert filename == "kx-new-zealand-2layers-JPEG-SHP.zip"
    finally:
        shutil.rmtree(td)


@responses.activate
def test_export_download_file_object(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_complete,
        status=200,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.state == "complete"
    assert (
        e.download_url
        == "https://test.koordinates.com/services/api/v1/exports/19/download/"
    )

    responses.add(
        responses.GET,
        e.download_url,
        body="some data",
        status=200,
        content_type="application/zip",
        adding_headers={
            "Content-Length": "9",
            "Content-Disposition": "attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip",
        },
    )

    with io.BytesIO() as f:
        filename = e.download(f)
        assert not f.closed
        assert filename == "kx-new-zealand-2layers-JPEG-SHP.zip"
        assert len(f.getvalue()) == 9


@responses.activate
def test_download_progress(client):
    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 19}),
        body=export_complete,
        status=200,
        content_type="application/json",
    )

    e = client.exports.get(19)
    assert e.state == "complete"
    assert (
        e.download_url
        == "https://test.koordinates.com/services/api/v1/exports/19/download/"
    )

    body_data = "data" * 100000

    responses.add(
        responses.GET,
        e.download_url,
        body=body_data,
        status=200,
        content_type="application/zip",
        adding_headers={
            "Content-Length": str(len(body_data)),
            "Content-Disposition": "attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip",
        },
    )

    callbacks = []

    def progress(written, total):
        callbacks.append((written, total))

    td = tempfile.mkdtemp()
    try:
        filename = e.download(td, progress_callback=progress)
        assert filename == "kx-new-zealand-2layers-JPEG-SHP.zip"
    finally:
        shutil.rmtree(td)

    assert len(callbacks) >= 2
    assert callbacks[0][0] == 0  # pre-download callback
    assert callbacks[0][1] == len(body_data)
    assert callbacks[-1][0] == len(body_data)
    assert callbacks[-1][1] == len(body_data)


@responses.activate
def test_export_creation(client):
    responses.add(
        responses.POST,
        client.get_url("EXPORT", "POST", "create"),
        body="",
        status=201,
        adding_headers={
            "Location": "https://test.koordinates.com/services/api/v1/exports/20/"
        },
    )

    responses.add(
        responses.GET,
        client.get_url("EXPORT", "GET", "single", {"id": 20}),
        body=creation_ok,
        status=200,
        content_type="application/json",
    )

    e = Export()
    e.name = "fred the export"
    e.set_formats(vector="application/x-zipped-shp", raster="image/jpeg")
    e.crs = "EPSG:2193"
    e.add_item(
        Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/")
    )
    e.add_item(
        Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"),
        color="#003399",
    )

    e = client.exports.create(e)
    assert e.id
    assert e.url
    assert e.name == "kx-fred-the-export"
    assert e.items == [
        {"item": "https://test.koordinates.com/services/api/v1/layers/3/"},
        {
            "item": "https://test.koordinates.com/services/api/v1/layers/1/",
            "color": "#003399",
        },
    ]
    assert e.formats == {"raster": "image/jpeg", "vector": "application/x-zipped-shp"}


@responses.activate
def test_export_creation_error(client):
    responses.add(
        responses.POST,
        client.get_url("EXPORT", "POST", "create"),
        body=validation_error,
        status=400,
        content_type="application/json",
    )

    e = Export()
    e.set_formats(vector="application/x-zipped-shp", raster="image/jpeg")
    e.crs = "EPSG:4326"
    e.extent = {
        "type": "MultiPolygon",
        "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]],
    }
    e.add_item(
        Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/")
    )
    e.add_item(
        Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"),
        color="#003399",
    )

    with pytest.raises(exceptions.BadRequest):
        client.exports.create(e)


@responses.activate
def test_export_set_formats(client):
    e = Export()
    e.set_formats(vector="application/x-zipped-shp", raster="image/jpeg")
    assert e.formats == {
        "vector": "application/x-zipped-shp",
        "raster": "image/jpeg",
    }
    e.set_formats(grid="image/tiff;subtype=geotiff", vector=None)
    assert e.formats == {
        "raster": "image/jpeg",
        "grid": "image/tiff;subtype=geotiff",
    }


@responses.activate
def test_export_validation_error(client):
    responses.add(
        responses.POST,
        client.get_url("EXPORT", "POST", "validate"),
        body=validation_error,
        status=200,
        content_type="application/json",
    )

    e = Export()
    e.set_formats(vector="application/x-zipped-shp", raster="image/jpeg")
    e.crs = "EPSG:4326"
    e.extent = {
        "type": "MultiPolygon",
        "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]],
    }
    e.add_item(
        Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/")
    )
    e.add_item(
        Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"),
        color="#003399",
    )

    r = client.exports.validate(e)
    assert isinstance(r, ExportValidationResponse)
    assert not r.is_valid
    assert len(r.items) == 2
    assert not r.items[1]["is_valid"]
    assert r.items[1]["invalid_reasons"] == ["outside-extent"]

    assert r.get_reasons() == {
        "https://test.koordinates.com/services/api/v1/layers/1/": ["outside-extent"],
        "https://test.koordinates.com/services/api/v1/layers/3/": ["outside-extent"],
    }


@responses.activate
def test_export_validation_ok(client):
    responses.add(
        responses.POST,
        client.get_url("EXPORT", "POST", "validate"),
        body=validation_ok,
        status=200,
        content_type="application/json",
    )

    e = Export()
    e.set_formats(vector="application/x-zipped-shp", raster="image/jpeg")
    e.crs = "EPSG:4326"
    e.extent = None
    e.add_item(
        Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/")
    )
    e.add_item(
        Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"),
        color="#003399",
    )

    r = client.exports.validate(e)
    assert isinstance(r, ExportValidationResponse)
    assert r.is_valid
    assert len(r.items) == 2
    assert all(i["is_valid"] for i in r.items)
    assert r.get_reasons() == {}


@responses.activate
def test_export_format_options(client):
    responses.add(
        responses.OPTIONS,
        client.get_url("EXPORT", "OPTIONS", "options"),
        body=export_format_options,
        status=200,
        content_type="application/json",
    )

    formats = client.exports.get_formats()
    assert set(formats.keys()) == {"grid", "raster", "rat", "table", "vector"}
    assert set(formats["vector"]) == {
        "application/vnd.google-earth.kml+xml",
        "image/vnd.dwg",
        "application/x-ogc-gpkg",
        "application/x-ogc-mapinfo_file",
        "text/csv",
        "application/x-zipped-shp",
        "applicaton/x-ogc-filegdb",
    }


@responses.activate
def test_export_cancel(client):
    responses.add(
        responses.DELETE,
        client.get_url("EXPORT", "DELETE", "single", {"id": 20}),
        body=cancel_ok,
        status=202,
        content_type="application/json",
    )

    e = client.exports.cancel(20)
    assert e.id
    assert e.url
    assert e.state == "cancelled"


@responses.activate
def test_export_cancel_failed(client):
    responses.add(
        responses.DELETE,
        client.get_url("EXPORT", "DELETE", "single", {"id": 20}),
        body=cancel_error,
        status=409,
        content_type="application/json",
    )

    pytest.raises(exceptions.Conflict, client.exports.cancel, 20)


@responses.activate
def test_croplayer_list(client):
    responses.add(
        responses.GET,
        client.get_url("CROPLAYER", "GET", "multi"),
        body=croplayer_list,
        status=200,
        content_type="application/json",
    )

    r = client.exports.croplayers.list()
    crop_layer = r[0]
    assert isinstance(crop_layer, CropLayer)
    assert crop_layer.name == "NZ Topo50 Map Sheets"


@responses.activate
def test_croplayer_detail(client):
    responses.add(
        responses.GET,
        client.get_url("CROPLAYER", "GET", "single", {"id": 2}),
        body=croplayer_detail,
        status=200,
        content_type="application/json",
    )

    crop_layer = client.exports.croplayers.get(2)
    assert crop_layer.name == "NZ Topo50 Map Sheets"


@responses.activate
def test_cropfeature_list(client):
    responses.add(
        responses.GET,
        client.get_url("CROPLAYER", "GET", "single", {"id": 2}),
        body=croplayer_detail,
        status=200,
        content_type="application/json",
    )

    crop_layer = client.exports.croplayers.get(2)
    assert crop_layer.name == "NZ Topo50 Map Sheets"

    responses.add(
        responses.GET,
        client.get_url("CROPFEATURE", "GET", "multi", {"croplayer_id": 2}),
        body=cropfeature_list,
        status=200,
        content_type="application/json",
    )

    c = 0
    for f in crop_layer.list_features():
        c += 1

    assert c == 4
    assert f.name == "AS22"
    assert f.id == 442
    assert isinstance(f, CropFeature)


@responses.activate
def test_cropfeature_detail(client):
    responses.add(
        responses.GET,
        client.get_url(
            "CROPFEATURE", "GET", "single", {"croplayer_id": 2, "cropfeature_id": 442}
        ),
        body=cropfeature_detail,
        status=200,
        content_type="application/json",
    )

    f = client.exports.croplayers.get_feature(2, 442)

    assert f.name == "AS22"
    assert f.id == 442
    assert isinstance(f, CropFeature)
    assert f.geometry
