import base64
import json
import struct
from datetime import datetime, timedelta, timezone as dt_timezone
from unittest import mock

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from Watchman import ct
from Watchman.models import Client, CTLog, Match, NewCert, Search
from Watchman.tools import purge_new, run_cert_searches

KEY = ec.generate_private_key(ec.SECP256R1())
TIMESTAMP = 1795000000000


def make_cert(names, common_name=None):
    subject = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, common_name or names[0])]
    )
    issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test CA")])
    now = datetime(2026, 11, 20, tzinfo=dt_timezone.utc)
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(KEY.public_key())
        .serial_number(0xABC123)
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=90))
    )
    if names:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(n) for n in names]),
            critical=False,
        )
    return builder.sign(KEY, hashes.SHA256()).public_bytes(serialization.Encoding.DER)


def u24(data):
    return len(data).to_bytes(3, "big") + data


def timestamped_entry(der, precert):
    head = struct.pack(">QH", TIMESTAMP, 1 if precert else 0)
    if precert:
        # issuer key hash + a stand-in TBSCertificate
        return head + b"\x00" * 32 + u24(b"tbs") + b"\x00\x00"
    return head + u24(der) + b"\x00\x00"


def tile_leaf(der, precert=False):
    leaf = timestamped_entry(der, precert)
    if precert:
        leaf += u24(der)
    return leaf + struct.pack(">H", 32) + b"\x11" * 32


def get_entries_item(der, precert=False):
    leaf = b"\x00\x00" + timestamped_entry(der, precert)
    extra = u24(der) + u24(b"") if precert else u24(b"")
    return {
        "leaf_input": base64.b64encode(leaf).decode(),
        "extra_data": base64.b64encode(extra).decode(),
    }


class FakeResponse:
    def __init__(self, status=200, content=b"", headers=None):
        self.status_code = status
        self.content = content
        self.headers = headers or {}

    @property
    def text(self):
        return self.content.decode()

    def json(self):
        return json.loads(self.content)


class FakeSession:
    # Serves canned responses by URL; unknown URLs are 404
    def __init__(self, routes):
        self.routes = routes
        self.requested = []
        self.headers = {}

    def get(self, url, timeout=None):
        self.requested.append(url)
        route = self.routes.get(url)
        if callable(route):
            route = route(url)
        if route is None:
            return FakeResponse(404)
        if isinstance(route, FakeResponse):
            return route
        if isinstance(route, (dict, list)):
            route = json.dumps(route).encode()
        return FakeResponse(200, route)


LOG_LIST = {
    "operators": [
        {
            "name": "Tiles Inc",
            "logs": [
                {
                    "description": "Classic 2026",
                    "log_id": "classic-id",
                    "url": "https://classic.example/2026",
                    "state": {"usable": {}},
                    "temporal_interval": {
                        "start_inclusive": "2026-01-01T00:00:00Z",
                        "end_exclusive": "2027-01-01T00:00:00Z",
                    },
                },
                {
                    "description": "Retired 2025",
                    "log_id": "retired-id",
                    "url": "https://classic.example/2025/",
                    "state": {"retired": {}},
                },
                {
                    "description": "Over 2026h1",
                    "log_id": "over-id",
                    "url": "https://classic.example/2026h1/",
                    "state": {"usable": {}},
                    "temporal_interval": {
                        "start_inclusive": "2026-01-01T00:00:00Z",
                        "end_exclusive": "2026-07-01T00:00:00Z",
                    },
                },
            ],
            "tiled_logs": [
                {
                    "description": "Tiled 2026h2",
                    "log_id": "tiled-id",
                    "monitoring_url": "https://tiled.example/2026h2/",
                    "submission_url": "https://submit.example/2026h2/",
                    "state": {"qualified": {}},
                    "temporal_interval": {
                        "start_inclusive": "2026-07-01T00:00:00Z",
                        "end_exclusive": "2027-01-01T00:00:00Z",
                    },
                },
                {
                    "description": "Far off 2029",
                    "log_id": "future-id",
                    "monitoring_url": "https://tiled.example/2029/",
                    "state": {"usable": {}},
                    "temporal_interval": {
                        "start_inclusive": "2029-01-01T00:00:00Z",
                        "end_exclusive": "2029-07-01T00:00:00Z",
                    },
                },
            ],
        }
    ]
}
NOW = datetime(2026, 11, 20, tzinfo=dt_timezone.utc)


class ParsingTests(TestCase):
    def test_tile_path(self):
        self.assertEqual(ct.tile_path(0), "tile/data/000")
        self.assertEqual(ct.tile_path(67), "tile/data/067")
        self.assertEqual(ct.tile_path(1234067), "tile/data/x001/x234/067")

    def test_log_list_keeps_only_logs_taking_certs_now(self):
        logs = ct.parse_log_list(LOG_LIST, now=NOW)
        self.assertEqual(
            {log["log_id"]: log["is_tiled"] for log in logs},
            {"classic-id": False, "tiled-id": True},
        )
        by_id = {log["log_id"]: log for log in logs}
        self.assertEqual(by_id["classic-id"]["url"], "https://classic.example/2026/")
        self.assertEqual(by_id["tiled-id"]["url"], "https://tiled.example/2026h2/")

    def test_normalize_name(self):
        self.assertEqual(ct.normalize_name("WWW.Example.COM."), ("www.example.com", False))
        self.assertEqual(ct.normalize_name("*.example.com"), ("example.com", True))
        self.assertEqual(ct.normalize_name("xn--bcher-kva.example"), ("xn--bcher-kva.example", False))
        for bad in ("localhost", "bad name.com", "a..com", "-a.com", "x" * 254 + ".com", ""):
            self.assertIsNone(ct.normalize_name(bad), bad)

    def test_cert_rows_reads_san_names(self):
        der = make_cert(["login.example.com", "*.example.com", "LOGIN.example.com"])
        rows = ct.cert_rows(der, "Test Log", 7, TIMESTAMP, True)
        self.assertEqual(
            [(r["name"], r["is_wildcard"]) for r in rows],
            [("login.example.com", False), ("example.com", True)],
        )
        row = rows[0]
        self.assertEqual(row["tld"], "com")
        self.assertEqual(row["issuer"], "CN=Test CA")
        self.assertEqual(row["serial"], "abc123")
        self.assertEqual(row["log"], "Test Log")
        self.assertEqual(row["log_index"], 7)
        self.assertTrue(row["is_precert"])
        self.assertEqual(row["not_before"], NOW)
        self.assertEqual(
            row["logged_at"],
            datetime.fromtimestamp(TIMESTAMP / 1000, tz=dt_timezone.utc),
        )

    def test_cert_rows_falls_back_to_common_name(self):
        rows = ct.cert_rows(make_cert([], "cn.example.org"), "L", 0, TIMESTAMP, False)
        self.assertEqual([r["name"] for r in rows], ["cn.example.org"])

    def test_tile_leaf_round_trip(self):
        cert, precert = make_cert(["a.example.com"]), make_cert(["b.example.com"])
        tile = tile_leaf(cert) + tile_leaf(precert, precert=True)
        timestamp, is_precert, der, offset = ct.read_tile_leaf(tile, 0)
        self.assertEqual((timestamp, is_precert, der), (TIMESTAMP, False, cert))
        timestamp, is_precert, der, offset = ct.read_tile_leaf(tile, offset)
        self.assertEqual((is_precert, der), (True, precert))
        self.assertEqual(offset, len(tile))

    def test_merkle_tree_leaf_round_trip(self):
        cert = make_cert(["a.example.com"])
        for precert in (False, True):
            item = get_entries_item(cert, precert)
            parsed = ct.parse_merkle_tree_leaf(
                base64.b64decode(item["leaf_input"]),
                base64.b64decode(item["extra_data"]),
            )
            self.assertEqual(parsed, (TIMESTAMP, precert, cert))

    def test_truncated_entry_is_an_error(self):
        tile = tile_leaf(make_cert(["a.example.com"]))
        with self.assertRaises(ct.CTError):
            ct.read_tile_leaf(tile[:-40], 0)


def tile_bytes(first_index, count=ct.TILE_WIDTH, precert=False):
    return b"".join(
        tile_leaf(make_cert([f"host{first_index + i}.example.com"]), precert)
        for i in range(count)
    )


@override_settings(
    CT_LOG_LIST_URL="https://list.example/log_list.json",
    CT_MAX_ENTRIES_PER_LOG=256,
    CT_CONCURRENCY=2,
    CT_LOG_INCLUDE="",
    CT_LOG_EXCLUDE="",
)
class IngestTests(TestCase):
    def setUp(self):
        patcher = mock.patch("Watchman.ct.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch("Watchman.ct.timezone.now", return_value=NOW)
        patcher.start()
        self.addCleanup(patcher.stop)

    def ingest(self, routes, **kwargs):
        routes.setdefault("https://list.example/log_list.json", LOG_LIST)
        self.session = FakeSession(routes)
        with mock.patch("Watchman.ct.make_session", return_value=self.session):
            return ct.ingest_certs(upload=False, **kwargs)

    def test_reads_tiled_and_classic_logs(self):
        classic = [
            get_entries_item(make_cert([f"c{i}.example.net", "shared.example.net"]), i % 2)
            for i in range(3)
        ]
        stats = self.ingest(
            {
                "https://tiled.example/2026h2/checkpoint": b"tiled.example/2026h2\n600\nhash\n",
                # 600 entries: the window starts at 344, inside tile 1
                "https://tiled.example/2026h2/tile/data/001": tile_bytes(256, precert=True),
                "https://classic.example/2026/ct/v1/get-sth": {"tree_size": 3},
                "https://classic.example/2026/ct/v1/get-entries?start=0&end=2": {"entries": classic},
            }
        )
        self.assertEqual(stats["logs"], 2)
        self.assertEqual(stats["errors"], 0)
        self.assertEqual(stats["entries"], 259)
        self.assertEqual(stats["new_names"], 256 + 4)
        self.assertEqual(NewCert.objects.count(), 260)

        cert = NewCert.objects.get(name="host300.example.com")
        self.assertEqual(cert.log, "Tiled 2026h2")
        self.assertEqual(cert.log_index, 300)
        self.assertTrue(cert.is_precert)
        self.assertEqual(NewCert.objects.get(name="c2.example.net").log_index, 2)

        tiled = CTLog.objects.get(log_id="tiled-id")
        # The partial tile at the tip (512-600) waits for the next run
        self.assertEqual((tiled.position, tiled.tree_size, tiled.status), (512, 600, "good"))
        classic_log = CTLog.objects.get(log_id="classic-id")
        self.assertEqual((classic_log.position, classic_log.status), (3, "good"))
        # Logs not taking new certs aren't tracked
        self.assertEqual(CTLog.objects.count(), 2)

    def test_resumes_and_skips_ahead_when_far_behind(self):
        CTLog.objects.create(
            log_id="classic-id", name="Classic 2026", url="https://classic.example/2026/", position=3
        )
        CTLog.objects.create(log_id="tiled-id", name="Tiled 2026h2", url="https://tiled.example/2026h2/", is_tiled=True, enabled=False)
        requested = []

        def entries(url):
            requested.append(url)
            start = int(url.split("start=")[1].split("&")[0])
            # Serve one entry per request to exercise the short-response loop
            return {"entries": [get_entries_item(make_cert([f"r{start}.example.net"]))]}

        routes = {"https://classic.example/2026/ct/v1/get-sth": {"tree_size": 5}}
        for start in (3, 4):
            routes[f"https://classic.example/2026/ct/v1/get-entries?start={start}&end=4"] = entries
        stats = self.ingest(routes)
        self.assertEqual(stats["logs"], 1)  # the disabled log is left alone
        self.assertEqual(sorted(NewCert.objects.values_list("name", flat=True)), ["r3.example.net", "r4.example.net"])
        self.assertEqual(CTLog.objects.get(log_id="classic-id").position, 5)

        # The log jumps 1000 entries; only the newest 256 are read
        routes = {"https://classic.example/2026/ct/v1/get-sth": {"tree_size": 1005}}
        for start in range(749, 1005):
            end = min((start // 256 + 1) * 256, 1005) - 1
            routes[f"https://classic.example/2026/ct/v1/get-entries?start={start}&end={end}"] = entries
        stats = self.ingest(routes)
        self.assertEqual(stats["skipped"], 744)
        self.assertEqual(stats["entries"], 256)
        log = CTLog.objects.get(log_id="classic-id")
        self.assertEqual((log.position, log.entries_skipped), (1005, 744))
        self.assertFalse(NewCert.objects.filter(name="r5.example.net").exists())
        self.assertTrue(NewCert.objects.filter(name="r749.example.net").exists())

    def test_known_names_are_not_added_again(self):
        NewCert.objects.create(name="host0.example.com", tld="com", log="earlier")
        stats = self.ingest(
            {
                "https://tiled.example/2026h2/checkpoint": b"o\n256\nh\n",
                "https://tiled.example/2026h2/tile/data/000": tile_bytes(0),
                "https://classic.example/2026/ct/v1/get-sth": {"tree_size": 0},
            },
        )
        self.assertEqual(stats["new_names"], 255)
        self.assertEqual(NewCert.objects.get(name="host0.example.com").log, "earlier")

    def test_log_failure_is_recorded_and_others_continue(self):
        bad_tile = tile_bytes(0, count=10)  # truncated tile
        stats = self.ingest(
            {
                "https://tiled.example/2026h2/checkpoint": b"o\n256\nh\n",
                "https://tiled.example/2026h2/tile/data/000": bad_tile,
                "https://classic.example/2026/ct/v1/get-sth": {"tree_size": 1},
                "https://classic.example/2026/ct/v1/get-entries?start=0&end=0": {
                    "entries": [get_entries_item(make_cert(["ok.example.net"]))]
                },
            }
        )
        self.assertEqual(stats["errors"], 1)
        tiled = CTLog.objects.get(log_id="tiled-id")
        self.assertEqual((tiled.status, tiled.position), ("error", 0))
        self.assertIn("truncated", tiled.error_message)
        self.assertTrue(NewCert.objects.filter(name="ok.example.net").exists())

    def test_missing_tile_is_retried_next_run(self):
        stats = self.ingest(
            {
                "https://tiled.example/2026h2/checkpoint": b"o\n256\nh\n",
                "https://classic.example/2026/ct/v1/get-sth": FakeResponse(500),
            }
        )
        tiled = CTLog.objects.get(log_id="tiled-id")
        self.assertEqual((tiled.status, tiled.position), ("good", 0))
        # A log that keeps answering 500 is an error, after retries
        self.assertEqual(stats["errors"], 1)
        self.assertEqual(CTLog.objects.get(log_id="classic-id").status, "error")
        self.assertEqual(
            self.session.requested.count("https://classic.example/2026/ct/v1/get-sth"),
            ct.HTTP_TRIES,
        )

    def test_unparseable_cert_is_counted_not_fatal(self):
        stats = self.ingest(
            {
                "https://tiled.example/2026h2/checkpoint": b"o\n0\nh\n",
                "https://classic.example/2026/ct/v1/get-sth": {"tree_size": 2},
                "https://classic.example/2026/ct/v1/get-entries?start=0&end=1": {
                    "entries": [
                        get_entries_item(b"not a certificate"),
                        get_entries_item(make_cert(["fine.example.net"])),
                    ]
                },
            }
        )
        self.assertEqual((stats["entries"], stats["unparseable"], stats["new_names"]), (2, 1, 1))

    def test_log_filter_and_unreachable_log_list(self):
        CTLog.objects.create(log_id="a", name="Alpha", url="https://a.example/")
        CTLog.objects.create(log_id="b", name="Beta", url="https://b.example/")
        stats = self.ingest(
            {
                "https://list.example/log_list.json": FakeResponse(404),
                "https://a.example/ct/v1/get-sth": {"tree_size": 0},
            },
            include="alpha",
        )
        self.assertEqual((stats["logs"], stats["errors"]), (1, 0))
        self.assertNotIn("https://b.example/ct/v1/get-sth", self.session.requested)

    def test_new_names_are_uploaded_as_a_list(self):
        routes = {
            "https://list.example/log_list.json": LOG_LIST,
            "https://tiled.example/2026h2/checkpoint": b"o\n256\nh\n",
            "https://tiled.example/2026h2/tile/data/000": tile_bytes(0),
            "https://classic.example/2026/ct/v1/get-sth": {"tree_size": 0},
        }
        s3 = mock.Mock()
        with mock.patch("Watchman.ct.make_session", return_value=FakeSession(routes)), mock.patch(
            "Watchman.tools.get_s3_client", return_value=s3
        ), self.settings(NEWCERT_BUCKET_NAME="bucket", MIN_DOMAIN_LIST_LENGTH=10):
            stats = ct.ingest_certs()
        self.assertEqual(stats["list_key"], "certs/20261120-000000.txt")
        kwargs = s3.put_object.call_args.kwargs
        self.assertEqual((kwargs["Bucket"], kwargs["Key"]), ("bucket", stats["list_key"]))
        self.assertEqual(len(kwargs["Body"].split()), 256)


class SearchTests(TestCase):
    def setUp(self):
        self.client_org = Client.objects.create(name="Acme", domain="acme.example")
        for name in ("acme-login.example.com", "login.acme.evil.net", "unrelated.org"):
            NewCert.objects.create(name=name, tld=name.rsplit(".", 1)[-1])
        NewCert.objects.create(name="acme.ignored.com", tld="com", is_ignored=True)
        for target in ("has_mx", "has_website"):
            patcher = mock.patch(f"Watchman.tools.{target}", return_value=False)
            patcher.start()
            self.addCleanup(patcher.stop)

    def add_search(self, database, method="substring", criteria="acme"):
        return Search.objects.create(
            client=self.client_org, database=database, method=method, criteria=criteria
        )

    def test_newcerts_search_matches_cert_names_once(self):
        search = self.add_search("newcerts")
        self.assertEqual(run_cert_searches(), 3)
        self.assertEqual(
            sorted(Match.objects.values_list("domain", flat=True)),
            ["acme-login.example.com", "login.acme.evil.net"],
        )
        self.assertEqual(Match.objects.first().search, search)
        self.assertFalse(NewCert.objects.filter(is_processed=False, is_ignored=False).exists())
        # Nothing left to search, and no duplicate matches
        self.assertEqual(run_cert_searches(), 0)
        self.assertEqual(Match.objects.count(), 2)

    def test_chunks_cover_every_name(self):
        self.add_search("all", method="regex", criteria=r".*acme")
        self.assertEqual(run_cert_searches(chunk_size=2), 3)
        self.assertEqual(Match.objects.count(), 2)

    def test_newdomains_searches_skip_certs_unless_enabled(self):
        self.add_search("newdomains")
        self.assertEqual(run_cert_searches(), 0)
        self.assertEqual(Match.objects.count(), 0)
        # Names stay unprocessed until a search covers them
        self.assertEqual(NewCert.objects.filter(is_processed=True).count(), 0)
        with self.settings(CT_MATCH_NEWDOMAIN_SEARCHES=True):
            self.assertEqual(run_cert_searches(), 3)
        self.assertEqual(Match.objects.count(), 2)

    @override_settings(CT_MAX_CERT_AGE=30, MAX_NEW_AGE=400)
    def test_purge_new_drops_old_cert_names(self):
        NewCert.objects.filter(name="unrelated.org").update(
            created=timezone.now() - timedelta(days=31)
        )
        purge_new()
        self.assertFalse(NewCert.objects.filter(name="unrelated.org").exists())
        self.assertEqual(NewCert.objects.count(), 3)


class ViewTests(TestCase):
    def setUp(self):
        for i in range(5):
            NewCert.objects.create(name=f"site{i}.example.com", tld="com", issuer="CN=Test CA", log="Test Log")
        NewCert.objects.create(name="wild.example.org", tld="org", is_wildcard=True)
        NewCert.objects.create(name="hidden.example.com", tld="com", is_ignored=True)
        User = get_user_model()
        self.user = User.objects.create(**{User.USERNAME_FIELD: "user@example.com"})

    def test_requires_login(self):
        for url in ("/newcerts/", "/api/newcerts/"):
            self.assertEqual(self.client.get(url).status_code, 302, url)

    def test_html_list_and_filter(self):
        self.client.force_login(self.user)
        response = self.client.get("/newcerts/")
        self.assertContains(response, "site3.example.com")
        self.assertContains(response, "*.wild.example.org")
        self.assertNotContains(response, "hidden.example.com")
        response = self.client.get("/newcerts/?q=WILD")
        self.assertContains(response, "wild.example.org")
        self.assertNotContains(response, "site3.example.com")
        self.assertContains(self.client.get("/newcerts/?q=nothing"), "No new certificates")

    def test_json_and_paging(self):
        self.client.force_login(self.user)
        data = self.client.get("/api/newcerts/?per_page=4&page=2").json()
        self.assertEqual((data["count"], data["total"], data["page"], data["pages"]), (2, 6, 2, 2))
        data = self.client.get("/newcerts/?format=json&q=site1&per_page=junk").json()
        self.assertEqual([r["name"] for r in data["results"]], ["site1.example.com"])
        self.assertEqual(data["results"][0]["issuer"], "CN=Test CA")

    def test_search_api(self):
        self.client.force_login(self.user)
        data = self.client.get("/api/search/?search_type=new_cert&value=wild").json()
        self.assertEqual([r["name"] for r in data["results"]], ["wild.example.org"])
