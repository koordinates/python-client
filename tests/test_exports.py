#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_exports
----------------------------------

Tests for the `koordinates.exports` module.
"""
from __future__ import unicode_literals, absolute_import

import io
import os
import shutil
import tempfile
import unittest

import responses

#from koordinates import api
from koordinates import exceptions
from koordinates import Client, Export, Layer, DownloadError
from koordinates.exports import ExportValidationResponse, CropLayer, CropFeature

from response_data.exports import creation_ok, validation_ok, validation_error, \
    cancel_ok, cancel_error, \
    croplayer_list, cropfeature_list, croplayer_detail, cropfeature_detail, \
    export_list, export_detail, export_complete, export_format_options


class TestExports(unittest.TestCase):
    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')

    @responses.activate
    def test_export_list(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'multi'),
            body=export_list, status=200,
            content_type='application/json')

        export_count = 0
        for e in self.client.exports.list():
            export_count += 1
            if e == 0:
                self.assertEqual(e.id, 19)
                self.assertEqual(e.name, "kx-new-zealand-2layers-JPEG-SHP")
                self.assertEqual(e.created_at.isoformat(), "2016-04-20T22:31:19.242850+00:00")
                self.assertEqual(e.created_via, "web")
                self.assertEqual(e.state, "complete")
                self.assertEqual(e.url, "https://test.koordinates.com/services/api/v1/exports/19/")
                self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")

        self.assertEqual(export_count, 5)

    @responses.activate
    def test_export_detail(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_complete, status=303,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.id, 19)
        self.assertEqual(e.name, "kx-new-zealand-2layers-JPEG-SHP")
        self.assertEqual(e.created_at.isoformat(), "2016-04-20T22:31:19.242850+00:00")
        self.assertEqual(e.created_via, "web")
        self.assertEqual(e.state, "complete")
        self.assertEqual(e.url, "https://test.koordinates.com/services/api/v1/exports/19/")
        self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")
        self.assertEqual(e.extent, None)
        self.assertEqual(e.delivery, {"method": "download"})
        self.assertEqual(e.formats, {"raster": "image/jpeg", "vector": "application/x-zipped-shp"})
        self.assertEqual(len(e.items), 2)
        self.assertEqual(e.options, {})
        self.assertEqual(e.crs, "EPSG:2193")
        self.assertEqual(e.size_estimate_zipped, 1905906)
        self.assertEqual(e.progress, 1.0)

    @responses.activate
    def test_export_download(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_complete, status=200,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.state, "complete")
        self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")

        responses.add(responses.GET,
            e.download_url,
            body='some data', status=200,
            content_type='application/zip',
            adding_headers={
                'Content-Length': '9',
                'Content-Disposition': 'attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip',
            })

        td = tempfile.mkdtemp()
        try:
            filename = e.download(td)
            self.assertEqual(filename, 'kx-new-zealand-2layers-JPEG-SHP.zip')
        finally:
            shutil.rmtree(td)

    @responses.activate
    def test_export_download_unavailable(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_detail, status=200,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.state, "processing")
        self.assertEqual(e.download_url, None)

        self.assertRaises(DownloadError, e.download, tempfile.tempdir)

    @responses.activate
    def test_export_download_filename(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_complete, status=200,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.state, "complete")
        self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")

        responses.add(responses.GET,
            e.download_url,
            body='some data', status=200,
            content_type='application/zip',
            adding_headers={
                'Content-Length': '9',
                'Content-Disposition': 'attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip',
            })

        td = tempfile.mkdtemp()
        try:
            tf = os.path.join(td, 'filey.mcfileface')
            filename = e.download(tf)
            assert os.path.isfile(tf)
            self.assertEqual(os.path.getsize(tf), 9)
            self.assertEqual(filename, 'kx-new-zealand-2layers-JPEG-SHP.zip')
        finally:
            shutil.rmtree(td)

    @responses.activate
    def test_export_download_file_object(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_complete, status=200,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.state, "complete")
        self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")

        responses.add(responses.GET,
            e.download_url,
            body='some data', status=200,
            content_type='application/zip',
            adding_headers={
                'Content-Length': '9',
                'Content-Disposition': 'attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip',
            })

        with io.BytesIO() as f:
            filename = e.download(f)
            assert not f.closed
            self.assertEqual(filename, 'kx-new-zealand-2layers-JPEG-SHP.zip')
            self.assertEqual(len(f.getvalue()), 9)

    @responses.activate
    def test_download_progress(self):
        responses.add(responses.GET,
            self.client.get_url('EXPORT', 'GET', 'single', {'id': 19}),
            body=export_complete, status=200,
            content_type='application/json')

        e = self.client.exports.get(19)
        self.assertEqual(e.state, "complete")
        self.assertEqual(e.download_url, "https://test.koordinates.com/services/api/v1/exports/19/download/")

        body_data = ('data' * 100000)

        responses.add(responses.GET,
            e.download_url,
            body=body_data, status=200,
            content_type='application/zip',
            adding_headers={
                'Content-Length': str(len(body_data)),
                'Content-Disposition': 'attachment; filename=kx-new-zealand-2layers-JPEG-SHP.zip',
            })

        callbacks = []
        def progress(written, total):
            callbacks.append((written, total))

        td = tempfile.mkdtemp()
        try:
            filename = e.download(td, progress_callback=progress)
            self.assertEqual(filename, "kx-new-zealand-2layers-JPEG-SHP.zip")
        finally:
            shutil.rmtree(td)

        assert len(callbacks) >= 2
        self.assertEqual(callbacks[0][0], 0)  # pre-download callback
        self.assertEqual(callbacks[0][1], len(body_data))
        self.assertEqual(callbacks[-1][0], len(body_data))
        self.assertEqual(callbacks[-1][1], len(body_data))

    @responses.activate
    def test_export_creation(self):
        responses.add(responses.POST,
          self.client.get_url('EXPORT', 'POST', 'create'),
          body="", status=302, adding_headers={"Location": "https://test.koordinates.com/services/api/v1/exports/20/"})

        responses.add(responses.GET,
          self.client.get_url('EXPORT', 'GET', 'single', {'id': 20}),
          body=creation_ok, status=200,
          content_type='application/json')

        e = Export()
        e.name = 'fred the export'
        e.set_formats(vector='application/x-zipped-shp', raster='image/jpeg')
        e.crs = 'EPSG:2193'
        e.add_item(Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/"))
        e.add_item(Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"), color="#003399")

        e = self.client.exports.create(e)
        assert e.id
        assert e.url
        self.assertEqual(e.name, 'kx-fred-the-export')
        self.assertEqual(e.items, [
            {
                "item": "https://test.koordinates.com/services/api/v1/layers/3/"
            },
            {
                "item": "https://test.koordinates.com/services/api/v1/layers/1/",
                "color": "#003399"
            },
        ])
        self.assertEqual(e.formats, {"raster": "image/jpeg", "vector": "application/x-zipped-shp"})

    @responses.activate
    def test_export_creation_error(self):
        responses.add(responses.POST,
            self.client.get_url('EXPORT', 'POST', 'create'),
            body=validation_error, status=400,
            content_type='application/json')

        e = Export()
        e.set_formats(vector='application/x-zipped-shp', raster='image/jpeg')
        e.crs = 'EPSG:4326'
        e.extent = {
            "type": "MultiPolygon",
            "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]],
        }
        e.add_item(Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/"))
        e.add_item(Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"), color="#003399")

        with self.assertRaises(exceptions.BadRequest):
            self.client.exports.create(e)

    @responses.activate
    def test_export_set_formats(self):
        e = Export()
        e.set_formats(vector='application/x-zipped-shp', raster='image/jpeg')
        self.assertEqual(e.formats, {
            'vector': 'application/x-zipped-shp',
            'raster': 'image/jpeg',
        })
        e.set_formats(grid='image/tiff', vector=None)
        self.assertEqual(e.formats, {
            'raster': 'image/jpeg',
            'grid': 'image/tiff',
        })

    @responses.activate
    def test_export_validation_error(self):
        responses.add(responses.POST,
            self.client.get_url('EXPORT', 'POST', 'validate'),
            body=validation_error, status=200,
            content_type='application/json')

        e = Export()
        e.set_formats(vector='application/x-zipped-shp', raster='image/jpeg')
        e.crs = 'EPSG:4326'
        e.extent = {
            "type": "MultiPolygon",
            "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]],
        }
        e.add_item(Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/"))
        e.add_item(Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"), color="#003399")

        r = self.client.exports.validate(e)
        self.assertIsInstance(r, ExportValidationResponse)
        assert not r.is_valid
        self.assertEqual(len(r.items), 2)
        assert not r.items[1]['is_valid']
        self.assertEqual(r.items[1]['invalid_reasons'], ['outside-extent'])

        self.assertEqual(r.get_reasons(), {
            "https://test.koordinates.com/services/api/v1/layers/1/": ['outside-extent'],
            "https://test.koordinates.com/services/api/v1/layers/3/": ['outside-extent'],
        })

    @responses.activate
    def test_export_validation_ok(self):
        responses.add(responses.POST,
            self.client.get_url('EXPORT', 'POST', 'validate'),
            body=validation_ok, status=200,
            content_type='application/json')

        e = Export()
        e.set_formats(vector='application/x-zipped-shp', raster='image/jpeg')
        e.crs = 'EPSG:4326'
        e.extent = None
        e.add_item(Layer(id=3, url="https://test.koordinates.com/services/api/v1/layers/3/"))
        e.add_item(Layer(id=1, url="https://test.koordinates.com/services/api/v1/layers/1/"), color="#003399")

        r = self.client.exports.validate(e)
        self.assertIsInstance(r, ExportValidationResponse)
        assert r.is_valid
        self.assertEqual(len(r.items), 2)
        assert all(i['is_valid'] for i in r.items)
        self.assertEqual(r.get_reasons(), {})

    @responses.activate
    def test_export_format_options(self):
        responses.add(responses.OPTIONS,
            self.client.get_url('EXPORT', 'OPTIONS', 'options'),
            body=export_format_options, status=200,
            content_type='application/json')

        formats = self.client.exports.get_formats()
        self.assertEqual(set(formats.keys()), set(["grid", "raster", "rat", "table", "vector"]))
        self.assertEqual(set(formats['vector']), set([
            'application/vnd.google-earth.kml+xml',
            'image/vnd.dwg',
            'application/x-ogc-gpkg',
            'application/x-ogc-mapinfo_file',
            'text/csv',
            'application/x-zipped-shp',
            'applicaton/x-ogc-filegdb',
        ]))


    @responses.activate
    def test_export_cancel(self):
        responses.add(responses.DELETE,
          self.client.get_url('EXPORT', 'DELETE', 'single', {'id': 20}),
          body=cancel_ok, status=202,
          content_type='application/json')

        e = self.client.exports.cancel(20)
        assert e.id
        assert e.url
        self.assertEqual(e.state, 'cancelled')

    @responses.activate
    def test_export_cancel_failed(self):
        responses.add(responses.DELETE,
          self.client.get_url('EXPORT', 'DELETE', 'single', {'id': 20}),
          body=cancel_error, status=409,
          content_type='application/json')

        self.assertRaises(exceptions.Conflict, self.client.exports.cancel, 20)

    @responses.activate
    def test_croplayer_list(self):
        responses.add(responses.GET,
          self.client.get_url('CROPLAYER', 'GET', 'multi'),
          body=croplayer_list, status=200,
          content_type='application/json')

        r = self.client.exports.croplayers.list()
        crop_layer = r[0]
        self.assertIsInstance(crop_layer, CropLayer)
        self.assertEqual(crop_layer.name, "NZ Topo50 Map Sheets")

    @responses.activate
    def test_croplayer_detail(self):
        responses.add(responses.GET,
          self.client.get_url('CROPLAYER', 'GET', 'single', {'id': 2}),
          body=croplayer_detail, status=200,
          content_type='application/json')

        crop_layer = self.client.exports.croplayers.get(2)
        self.assertEqual(crop_layer.name, "NZ Topo50 Map Sheets")

    @responses.activate
    def test_cropfeature_list(self):
        responses.add(responses.GET,
          self.client.get_url('CROPLAYER', 'GET', 'single', {'id': 2}),
          body=croplayer_detail, status=200,
          content_type='application/json')

        crop_layer = self.client.exports.croplayers.get(2)
        self.assertEqual(crop_layer.name, "NZ Topo50 Map Sheets")

        responses.add(responses.GET,
          self.client.get_url('CROPFEATURE', 'GET', 'multi', {'croplayer_id': 2}),
          body=cropfeature_list, status=200,
          content_type='application/json')

        c = 0
        for f in crop_layer.list_features():
            c += 1

        self.assertEqual(c, 4)
        self.assertEqual(f.name, "AS22")
        self.assertEqual(f.id, 442)
        self.assertIsInstance(f, CropFeature)

    @responses.activate
    def test_cropfeature_detail(self):
        responses.add(responses.GET,
          self.client.get_url('CROPFEATURE', 'GET', 'single', {'croplayer_id': 2, 'cropfeature_id': 442}),
          body=cropfeature_detail, status=200,
          content_type='application/json')

        f = self.client.exports.croplayers.get_feature(2, 442)

        self.assertEqual(f.name, "AS22")
        self.assertEqual(f.id, 442)
        self.assertIsInstance(f, CropFeature)
        assert f.geometry

