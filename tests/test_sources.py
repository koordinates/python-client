import json
import os
import tempfile
import types
import unittest
from StringIO import StringIO

from requests_toolbelt import MultipartEncoderMonitor, MultipartDecoder
import responses
import six

from koordinates import Source, Client, Group, User, BadRequest, UploadSource

from response_data.sources import (
    source_list, source_detail,
    source_create_arcgis, source_create_arcgis_bad_remote,
    source_create_upload_single, source_create_upload_multiple,
    source_scan_list, source_scan_detail, source_scan_log,
)


class TestSources(unittest.TestCase):
    CSV_DATA = (
        'ID,NAME,AGE\r\n'
        '1,"Alice",33\r\n'
        '2,"Bob",29\r\n'
    )

    def setUp(self):
        self.client = Client(token='test', host='test.koordinates.com')

    @responses.activate
    def test_list(self):
        responses.add(responses.GET,
                      self.client.get_url('SOURCE', 'GET', 'multi'),
                      body=source_list, status=200,
                      content_type='application/json')

        for i, source in enumerate(self.client.sources.list()):
            if i == 0:
                self.assertEqual(source.id, 21836)
                self.assertEqual(source.url, "https://test.koordinates.com/services/api/v1/sources/21836/")
                self.assertEqual(source.type, Source.TYPE_UPLOAD)
                self.assertEqual(source.title, "nzdf-built-up-area-area-feature-SHP.zip")
                self.assert_(source._is_bound)
        self.assertEqual(i+1, 4)  # count

    @responses.activate
    def test_detail(self):
        responses.add(responses.GET,
                      self.client.get_url('SOURCE', 'GET', 'single', {'id':21836}),
                      body=source_detail, status=200,
                      content_type='application/json')

        source = self.client.sources.get(21836)

        self.assert_(isinstance(source, Source))
        self.assert_(source._is_bound)

        self.assertEqual(source.id, 21836)
        self.assertEqual(source.url, "https://test.koordinates.com/services/api/v1/sources/21836/")
        self.assertEqual(source.type, Source.TYPE_UPLOAD)
        self.assertEqual(source.title, "nzdf-built-up-area-area-feature-SHP.zip")
        self.assertEqual(source.license, None)
        self.assertEqual(source.publish_to_catalog_services, False)
        self.assertEqual(source.permissions, "https://test.koordinates.com/services/api/v1/sources/21836/permissions/")
        self.assertEqual(source.description, "Upload: nzdf-built-up-area-area-feature-SHP.zip")
        self.assertEqual(source.description_html, "<p>Upload: nzdf-built-up-area-area-feature-SHP.zip</p>")
        self.assertEqual(source.categories, [])
        self.assertEqual(source.tags, [])
        self.assert_(isinstance(source.group, Group))
        self.assertEqual(source.group.id, 371)
        self.assertEqual(source.metadata, None)
        self.assertEqual(source.last_scanned_at, None)
        self.assertEqual(source.scan_schedule, None)
        self.assertEqual(source.options, {})

    @responses.activate
    def test_create(self):
        responses.add(responses.POST,
            self.client.get_url('SOURCE', 'POST', 'create'),
            body=source_create_arcgis, status=200,
            content_type='application/json')

        source = Source()
        source.title = "Bob's ArcGIS 10 Server"
        source.type = Source.TYPE_ARCGIS
        source.description = "All of Bob's data"
        source.categories = []
        source.user = 3
        source.url_remote = "http://server.arcgisonline.com/ArcGIS/rest/services"
        source.scan_schedule = "@daily"
        source.options = {
            "username": "bob",
            "password": "sekret_p@55w0rd"
        }

        source = self.client.sources.create(source)

        self.assertEqual(source.id, 58)
        self.assertEqual(source.url, "https://test.koordinates.com/services/api/v1/sources/58/")
        self.assertEqual(source.title, "Bob's ArcGIS 10 Server")
        self.assertEqual(source.type, "arcgis")
        self.assertEqual(source.license, None)
        self.assertEqual(source.publish_to_catalog_services, False)
        self.assertEqual(source.permissions, "https://test.koordinates.com/services/api/v1/sources/58/permissions/")
        self.assertEqual(source.description, "All of Bob's data")
        self.assertEqual(source.description_html, "<p>All of Bob's data</p>")
        self.assertEqual(source.categories, [])
        self.assertEqual(source.tags, [])
        self.assert_(isinstance(source.user, User))
        self.assertEqual(source.user.id, 3)
        self.assertEqual(source.metadata, None)
        self.assertEqual(source.last_scanned_at, None)
        self.assertEqual(source.scan_schedule, None)
        self.assertEqual(source.options, {})
        self.assertEqual(source.url_remote, "http://server.arcgisonline.com/ArcGIS/rest/services")

    @responses.activate
    def test_create_bad_url(self):
        responses.add(responses.POST,
            self.client.get_url('SOURCE', 'POST', 'create'),
            body=source_create_arcgis_bad_remote, status=400,
            content_type='application/json')

        source = Source()
        source.title = "Bob's ArcGIS 10 Server"
        source.type = Source.TYPE_ARCGIS
        source.description = "All of Bob's data"
        source.categories = []
        source.user = 3
        source.url_remote = "http://bad.example.com/ArcGIS/rest/services"
        source.options = {}

        try:
            source = self.client.sources.create(source)
        except BadRequest as e:
            self.assertEqual(e.message, "url_remote: Invalid URL: Can't resolve host.")
        else:
            assert False, "Expected to raise BadRequest"

    @responses.activate
    def test_create_upload_single(self):
        responses.add(responses.POST,
            self.client.get_url('SOURCE', 'POST', 'create'),
            body=source_create_upload_single, status=200,
            content_type='application/json')

        source = UploadSource()
        source.title = "Test single-file upload"
        f = StringIO(self.CSV_DATA)
        f.name = 'test.csv'
        source.add_file(f)

        source = self.client.sources.create(source)

        req = responses.calls[0].request
        # Check we have multipart data
        self.assert_(req.headers['Content-Type'].startswith('multipart/form-data; boundary='))

        assert isinstance(req.body, MultipartEncoderMonitor)
        #stringify - this consumes the data too

        decoder = MultipartDecoder(req.body.to_string(), req.headers['Content-Type'])
        self.assertEqual(len(decoder.parts), 2)

        parts = sorted([(dict(p.headers), p.text) for p in decoder.parts])
        self.assertEqual(parts, sorted([
            (
                {'Content-Type': 'application/json', 'Content-Disposition': 'form-data; name="source"'},
                json.dumps({"type": "upload", "title": "Test single-file upload"}),
            ),
            (
                {'Content-Type': 'text/csv', 'Content-Disposition': 'form-data; name="file0"; filename="test.csv"'},
                self.CSV_DATA,
            )
        ]))

    @responses.activate
    def test_create_upload_multiple(self):
        def req_callback(request):
            # need this to make sure the request body is consumed
            assert isinstance(request.body, MultipartEncoderMonitor)
            request.body = request.body.to_string()
            return (200, {}, source_create_upload_multiple)

        responses.add_callback(responses.POST,
            self.client.get_url('SOURCE', 'POST', 'create'),
            callback=req_callback,
            content_type='application/json')

        source = UploadSource()
        source.title = "Test multiple-file upload"

        f = StringIO(self.CSV_DATA)
        f.name = 'test11.csv'
        source.add_file(f)

        f = StringIO(self.CSV_DATA)
        f.name = 'test22.csv'
        source.add_file(f, upload_path='bob2.csv')

        f = StringIO(self.CSV_DATA)
        f.name = 'test33.csv'
        source.add_file(f, content_type='text/csv+fiz')

        f = StringIO(self.CSV_DATA)
        f.name = 'text44.csv'
        source.add_file(f, upload_path='bob4.csv', content_type='text/csv+fiz')

        ftemp = tempfile.NamedTemporaryFile(suffix='.csv')
        ftemp.write(self.CSV_DATA)
        ftemp.flush()
        source.add_file(ftemp.name)
        temp_filename = os.path.split(ftemp.name)[1]

        # request here
        source = self.client.sources.create(source)

        req = responses.calls[0].request
        # Check we have multipart data
        self.assert_(req.headers['Content-Type'].startswith('multipart/form-data; boundary='))

        decoder = MultipartDecoder(req.body, req.headers['Content-Type'])
        self.assertEqual(len(decoder.parts), 6)

        parts = sorted([(dict(p.headers), p.text) for p in decoder.parts])
        self.assertEqual(parts, sorted([
            (
                {'Content-Type': 'application/json', 'Content-Disposition': 'form-data; name="source"'},
                json.dumps({"type": "upload", "title": "Test multiple-file upload"}),
            ),
            (
                {'Content-Type': 'text/csv', 'Content-Disposition': 'form-data; name="file0"; filename="test11.csv"'},
                self.CSV_DATA,
            ),
            (
                {'Content-Type': 'text/csv', 'Content-Disposition': 'form-data; name="file1"; filename="bob2.csv"'},
                self.CSV_DATA,
            ),
            (
                {'Content-Type': 'text/csv+fiz', 'Content-Disposition': 'form-data; name="file2"; filename="test33.csv"'},
                self.CSV_DATA,
            ),
            (
                {'Content-Type': 'text/csv+fiz', 'Content-Disposition': 'form-data; name="file3"; filename="bob4.csv"'},
                self.CSV_DATA,
            ),
            (
                {'Content-Type': 'text/csv', 'Content-Disposition': 'form-data; name="file4"; filename="%s"' % temp_filename},
                self.CSV_DATA,
            ),
        ]))

    @responses.activate
    def test_scan_list(self):
        responses.add(responses.GET,
            self.client.get_url('SCAN', 'GET', 'multi', {'source_id': 44}),
            body=source_scan_list, status=200,
            content_type='text/plain')

        self.client.sources.list_scans('')

    @responses.activate
    def test_scan_detail(self):
        pass

    @responses.activate
    def test_scan_log_lines1(self):
        responses.add(responses.GET,
            self.client.get_url('SCAN', 'GET', 'log', {'source_id': 44, 'scan_id': 41}),
            body=source_scan_log, status=200,
            content_type='text/plain')

        r = self.client.sources.get_scan_log_lines(44, 41)
        self.assertIsInstance(r, types.GeneratorType)
        for i,line in enumerate(r):
            print repr(line)
            self.assertIsInstance(line, six.text_type)
            self.assert_(not line.endswith('\n'))
        self.assertEqual(i, 10)

    @responses.activate
    def test_scan_log_lines2(self):
        responses.add(responses.GET,
            self.client.get_url('SCAN', 'GET', 'single', {'source_id': 44, 'scan_id': 41}),
            body=source_scan_detail, status=200,
            content_type='text/plain')
        responses.add(responses.GET,
            self.client.get_url('SCAN', 'GET', 'log', {'source_id': 44, 'scan_id': 41}),
            body=source_scan_log, status=200,
            content_type='text/plain')

        scan = self.client.sources.get_scan(44, 41)
        r = scan.get_log_lines()
        self.assertIsInstance(r, types.GeneratorType)
        self.assertEqual(list(r), source_scan_log.strip().split('\n'))

