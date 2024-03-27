import json
import io
import os
import re
import tempfile
import types

import mimetypes
import pytest
from requests_toolbelt import MultipartEncoderMonitor, MultipartDecoder
import responses

from koordinates import Source, Client, Group, User, BadRequest, UploadSource
from koordinates.sources import Datasource, Scan
from koordinates.base import Query

from .response_data.sources import (
    source_list,
    source_detail,
    source_create_arcgis,
    source_create_arcgis_bad_remote,
    source_create_upload_single,
    source_create_upload_multiple,
    source_scan_list,
    source_scan_detail,
    source_scan_log,
    datasource_list,
    datasource_detail,
    datasource_detail_2,
    datasource_metadata,
)


CSV_DATA = "ID,NAME,AGE\r\n" '1,"Alice",33\r\n' '2,"Bob",29\r\n'


@pytest.fixture
def client():
    return Client(token="test", host="test.koordinates.com")


def assert_count_equal(a, b):
    """
    Asserts that the given sequence (list/set/whatever) has identical elements,
    ignoring order.
    analogous to: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertCountEqual
    """
    __tracebackhide__ = True

    for item in a:
        assert b.count(item) == a.count(item)


@responses.activate
def test_list(client):
    responses.add(
        responses.GET,
        client.get_url("SOURCE", "GET", "multi"),
        body=source_list,
        status=200,
        content_type="application/json",
    )

    for i, source in enumerate(client.sources.list()):
        if i == 0:
            assert source.id == 21836
            assert (
                source.url
                == "https://test.koordinates.com/services/api/v1/sources/21836/"
            )
            assert source.type == Source.TYPE_UPLOAD
            assert source.title == "nzdf-built-up-area-area-feature-SHP.zip"
            assert source._is_bound
    assert i + 1 == 4  # count


@responses.activate
def test_detail(client):
    responses.add(
        responses.GET,
        client.get_url("SOURCE", "GET", "single", {"id": 21836}),
        body=source_detail,
        status=200,
        content_type="application/json",
    )

    source = client.sources.get(21836)

    assert isinstance(source, Source)
    assert source._is_bound

    assert source.id == 21836
    assert source.url == "https://test.koordinates.com/services/api/v1/sources/21836/"
    assert source.type == Source.TYPE_UPLOAD
    assert source.title == "nzdf-built-up-area-area-feature-SHP.zip"
    assert source.license == None
    assert source.publish_to_catalog_services == False
    assert source.description == "Upload: nzdf-built-up-area-area-feature-SHP.zip"
    assert (
        source.description_html
        == "<p>Upload: nzdf-built-up-area-area-feature-SHP.zip</p>"
    )
    assert source.categories == []
    assert source.tags == []
    assert isinstance(source.group, Group)
    assert source.group.id, 371
    assert source.metadata == None
    assert source.last_scanned_at == None
    assert source.scan_schedule == None
    assert source.options == {}


@responses.activate
def test_create(client):
    responses.add(
        responses.POST,
        client.get_url("SOURCE", "POST", "create"),
        body=source_create_arcgis,
        status=201,
        content_type="application/json",
    )

    source = Source()
    source.title = "Bob's ArcGIS 10 Server"
    source.type = Source.TYPE_ARCGIS
    source.description = "All of Bob's data"
    source.categories = []
    source.user = 3
    source.url_remote = "http://server.arcgisonline.com/ArcGIS/rest/services"
    source.scan_schedule = "@daily"
    source.options = {"username": "bob", "password": "sekret_p@55w0rd"}

    source = client.sources.create(source)

    assert source.id == 58
    assert source.url == "https://test.koordinates.com/services/api/v1/sources/58/"
    assert source.title == "Bob's ArcGIS 10 Server"
    assert source.type == "arcgis"
    assert source.license == None
    assert source.publish_to_catalog_services == False
    assert source.description == "All of Bob's data"
    assert source.description_html == "<p>All of Bob's data</p>"
    assert source.categories == []
    assert source.tags == []
    assert isinstance(source.user, User)
    assert source.user.id == 3
    assert source.metadata == None
    assert source.last_scanned_at == None
    assert source.scan_schedule == None
    assert source.options == {}
    assert source.url_remote == "http://server.arcgisonline.com/ArcGIS/rest/services"


@responses.activate
def test_create_bad_url(client):
    responses.add(
        responses.POST,
        client.get_url("SOURCE", "POST", "create"),
        body=source_create_arcgis_bad_remote,
        status=400,
        content_type="application/json",
    )

    source = Source()
    source.title = "Bob's ArcGIS 10 Server"
    source.type = Source.TYPE_ARCGIS
    source.description = "All of Bob's data"
    source.categories = []
    source.user = 3
    source.url_remote = "http://bad.example.com/ArcGIS/rest/services"
    source.options = {}

    try:
        source = client.sources.create(source)
    except BadRequest as e:
        assert str(e) == "url_remote: Invalid URL: Can't resolve host."
    else:
        assert False, "Expected to raise BadRequest"


def _maybe_content_type(headers):
    # hack: the mimetypes module doesn't seem to work well in some distros
    # (-slim and -alpine variants of python docker images)
    if mimetypes.guess_type('a.csv') == (None, None):
        headers.pop(b'Content-Type')
    return headers


@responses.activate
def test_create_upload_single(client):
    responses.add(
        responses.POST,
        client.get_url("SOURCE", "POST", "create"),
        body=source_create_upload_single,
        status=201,
        content_type="application/json",
    )

    source = UploadSource()
    source.title = "Test single-file upload"
    f = io.StringIO(CSV_DATA)
    f.name = "test.csv"
    source.add_file(f)

    source = client.sources.create(source)

    req = responses.calls[0].request

    # Check we have multipart data
    assert re.match(r"^multipart/form-data; boundary=", req.headers["Content-Type"])
    assert isinstance(req.body, MultipartEncoderMonitor)
    # stringify - this consumes the data too

    decoder = MultipartDecoder(req.body.to_string(), req.headers["Content-Type"])
    assert len(decoder.parts) == 2

    parts = [(dict(p.headers), p.text) for p in decoder.parts]
    assert len(parts) == 2
    assert (
        {
            b"Content-Disposition": b'form-data; name="source"',
            b"Content-Type": b"application/json",
        },
        json.dumps({"type": "upload", "title": "Test single-file upload"}),
    ) in parts

    assert (
        _maybe_content_type(
            {
                b"Content-Disposition": b'form-data; name="file0"; filename="test.csv"',
                b"Content-Type": b"text/csv",
            }
        ),
        CSV_DATA,
    ) in parts


@responses.activate
def test_create_upload_multiple(client):
    def req_callback(request):
        # need this to make sure the request body is consumed
        assert isinstance(request.body, MultipartEncoderMonitor)
        request.body = request.body.to_string()
        return (201, {}, source_create_upload_multiple)

    responses.add_callback(
        responses.POST,
        client.get_url("SOURCE", "POST", "create"),
        callback=req_callback,
        content_type="application/json",
    )

    source = UploadSource()
    source.title = "Test multiple-file upload"

    f = io.StringIO(CSV_DATA)
    f.name = "test11.csv"
    source.add_file(f)

    f = io.StringIO(CSV_DATA)
    f.name = "test22.csv"
    source.add_file(f, upload_path="bob2.csv")

    f = io.StringIO(CSV_DATA)
    f.name = "test33.csv"
    source.add_file(f, content_type="text/csv+fiz")

    f = io.StringIO(CSV_DATA)
    f.name = "text44.csv"
    source.add_file(f, upload_path="bob4.csv", content_type="text/csv+fiz")

    ftemp = tempfile.NamedTemporaryFile(suffix=".csv", mode="w")
    ftemp.write(CSV_DATA)
    ftemp.flush()
    source.add_file(ftemp.name)
    temp_filename = os.path.split(ftemp.name)[1]

    # request here
    source = client.sources.create(source)

    req = responses.calls[0].request
    # Check we have multipart data
    assert re.match(r"^multipart/form-data; boundary=", req.headers["Content-Type"])

    decoder = MultipartDecoder(req.body, req.headers["Content-Type"])
    assert len(decoder.parts) == 6

    parts = [(dict(p.headers), p.text) for p in decoder.parts]
    assert_count_equal(
        parts,
        [
            (
                {
                    b"Content-Type": b"application/json",
                    b"Content-Disposition": b'form-data; name="source"',
                },
                json.dumps({"type": "upload", "title": "Test multiple-file upload"}),
            ),
            (
                _maybe_content_type(
                    {
                        b"Content-Type": b"text/csv",
                        b"Content-Disposition": b'form-data; name="file0"; filename="test11.csv"',
                    }
                ),
                CSV_DATA,
            ),
            (
                _maybe_content_type(
                    {
                        b"Content-Type": b"text/csv",
                        b"Content-Disposition": b'form-data; name="file1"; filename="bob2.csv"',
                    }
                ),
                CSV_DATA,
            ),
            (
                {
                    b"Content-Type": b"text/csv+fiz",
                    b"Content-Disposition": b'form-data; name="file2"; filename="test33.csv"',
                },
                CSV_DATA,
            ),
            (
                {
                    b"Content-Type": b"text/csv+fiz",
                    b"Content-Disposition": b'form-data; name="file3"; filename="bob4.csv"',
                },
                CSV_DATA,
            ),
            (
                _maybe_content_type(
                    {
                        b"Content-Type": b"text/csv",
                        b"Content-Disposition": (
                            'form-data; name="file4"; filename="%s"' % temp_filename
                        ).encode("utf-8"),
                    }
                ),
                CSV_DATA,
            ),
        ],
    )


@responses.activate
def test_scan_list(client):
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "multi", {"source_id": 44}),
        body=source_scan_list,
        status=200,
        content_type="application/json",
    )

    r = client.sources.list_scans(44)
    assert isinstance(r, Query)
    r = list(r)
    assert len(r) == 1
    assert isinstance(r[0], Scan)


@responses.activate
def test_source_scan_list(client):
    responses.add(
        responses.GET,
        client.get_url("SOURCE", "GET", "single", {"id": 21836}),
        body=source_detail,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "multi", {"source_id": 21836}),
        body=source_scan_list,
        status=200,
        content_type="application/json",
    )

    source = client.sources.get(21836)

    assert isinstance(source, Source)
    assert source._is_bound

    r = source.list_scans()
    assert isinstance(r, Query)
    r = list(r)
    assert len(r) == 1
    assert isinstance(r[0], Scan)


@responses.activate
def test_scan_detail(client):
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "single", {"source_id": 44, "scan_id": 41}),
        body=source_scan_detail,
        status=200,
        content_type="application/json",
    )

    scan = client.sources.get_scan(44, 41)
    assert isinstance(scan, Scan)
    assert scan.id == 41


@responses.activate
def test_scan_cancel(client):
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "single", {"source_id": 44, "scan_id": 41}),
        body=source_scan_detail,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.DELETE,
        client.get_url("SCAN", "DELETE", "cancel", {"source_id": 44, "scan_id": 41}),
        body="",
        status=204,
        content_type="application/json",
    )

    scan = client.sources.get_scan(44, 41)
    scan.cancel()

    assert len(responses.calls) == 2


@responses.activate
def test_scan_log_lines1(client):
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "log", {"source_id": 44, "scan_id": 41}),
        body=source_scan_log,
        status=200,
        content_type="text/plain",
    )

    r = client.sources.get_scan_log_lines(44, 41)
    assert isinstance(r, types.GeneratorType)
    for i, line in enumerate(r):
        assert isinstance(line, str)
        assert not line.endswith("\n")
    assert i == 10


@responses.activate
def test_scan_log_lines2(client):
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "single", {"source_id": 44, "scan_id": 41}),
        body=source_scan_detail,
        status=200,
        content_type="text/plain",
    )
    responses.add(
        responses.GET,
        client.get_url("SCAN", "GET", "log", {"source_id": 44, "scan_id": 41}),
        body=source_scan_log,
        status=200,
        content_type="text/plain",
    )

    scan = client.sources.get_scan(44, 41)
    r = scan.get_log_lines()
    assert isinstance(r, types.GeneratorType)
    assert list(r) == source_scan_log.strip().split("\n")


@responses.activate
def test_datasource_list(client):
    responses.add(
        responses.GET,
        client.get_url("DATASOURCE", "GET", "multi", {"source_id": 21838}),
        body=datasource_list,
        status=200,
        content_type="application/json",
    )

    r = client.sources.list_datasources(21838)
    assert isinstance(r, Query)
    r = list(r)
    assert len(r) == 1
    ds = r[0]
    assert isinstance(ds, Datasource)
    assert ds.id == 144187


@responses.activate
def test_source_datasource_list(client):
    responses.add(
        responses.GET,
        client.get_url("SOURCE", "GET", "single", {"id": 21836}),
        body=source_detail,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        client.get_url("DATASOURCE", "GET", "multi", {"source_id": 21836}),
        body=datasource_list,
        status=200,
        content_type="application/json",
    )

    source = client.sources.get(21836)

    assert isinstance(source, Source)
    assert source._is_bound

    r = source.list_datasources()
    assert isinstance(r, Query)
    r = list(r)
    assert len(r) == 1
    ds = r[0]
    assert isinstance(ds, Datasource)
    assert ds.id == 144187


@responses.activate
def test_datasource_detail(client):
    responses.add(
        responses.GET,
        client.get_url(
            "DATASOURCE", "GET", "single", {"source_id": 21838, "datasource_id": 144187}
        ),
        body=datasource_detail,
        status=200,
        content_type="application/json",
    )

    ds = client.sources.get_datasource(21838, 144187)
    assert isinstance(ds, Datasource)


@responses.activate
def test_datasource_metadata(client):
    responses.add(
        responses.GET,
        client.get_url(
            "DATASOURCE", "GET", "single", {"source_id": 55, "datasource_id": 167}
        ),
        body=datasource_detail_2,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        client.get_url(
            "DATASOURCE", "GET", "single", {"source_id": 55, "datasource_id": 167}
        )
        + "metadata/",
        body=datasource_metadata,
        status=200,
        content_type="text/xml",
    )

    ds = client.sources.get_datasource(55, 167)
    assert isinstance(ds, Datasource)
    assert ds.metadata

    s = io.BytesIO()
    ds.metadata.get_xml(s)
    metadata = s.getvalue().decode("utf-8")
    assert metadata[:16] == "<gmd:MD_Metadata"
    assert len(metadata) == 293
