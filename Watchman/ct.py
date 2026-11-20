# Certificate Transparency ingest: reads newly logged certificates from the
# public CT logs and records their hostnames as NewCert rows.
#
# Supports both log APIs: RFC 6962 (get-sth / get-entries) and the tiled
# static-ct-api (checkpoint / tile/data). Log signatures and inclusion proofs
# are not verified; this watches names, it doesn't audit logs.
import base64
import logging
import re
import struct
import tempfile
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone as dt_timezone
from time import monotonic, sleep

import requests
from cryptography import x509
from cryptography.x509.oid import NameOID
from django.conf import settings
from django.utils import timezone

from Watchman.models import CTLog, NewCert

logger = logging.getLogger(__name__)

TILE_WIDTH = 256
RFC6962_BATCH = 256
# Ranges fetched in parallel from one log in each round
RANGES_PER_LOG = 4
HTTP_TIMEOUT = 30
HTTP_TRIES = 4
STORE_CHUNK = 1000
# Certs are valid for under 400 days, so a shard starting later can't get any yet
MAX_CERT_LIFETIME = timedelta(days=400)

HOSTNAME_RE = re.compile(
    r"^(?:[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z0-9-]{2,63}$"
)


class CTError(Exception):
    pass


class NotReady(CTError):
    # The log advertised entries it isn't serving yet; try again next run
    pass


def make_session():
    session = requests.Session()
    agent = "Watchman-CT/1.0"
    if settings.CT_CONTACT:
        agent += f" (+{settings.CT_CONTACT})"
    session.headers["User-Agent"] = agent
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=64, pool_maxsize=settings.CT_CONCURRENCY
    )
    session.mount("https://", adapter)
    return session


def http_get(session, url, not_ready=()):
    # GET with backoff on rate limits and server errors. A status in not_ready
    # raises NotReady.
    status = None
    for attempt in range(HTTP_TRIES):
        try:
            response = session.get(url, timeout=HTTP_TIMEOUT)
        except requests.RequestException as e:
            status = f"{e}"
            sleep(2**attempt)
            continue
        status = response.status_code
        if status == 200:
            return response
        if status in not_ready:
            raise NotReady(f"HTTP {status} for {url}")
        if status == 429 or status >= 500:
            retry_after = response.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 2**attempt
            sleep(min(wait, 30))
            continue
        break
    raise CTError(f"{url}: {status}")


# --- Log list ---


def parse_log_list(data, now=None):
    # Returns the logs in Chrome's v3 log list that can take certificates
    # issued now: state usable or qualified, and a shard that isn't over or
    # too far off.
    now = now or timezone.now()
    logs = []
    for operator in data.get("operators", []):
        for key, is_tiled in (("logs", False), ("tiled_logs", True)):
            for raw in operator.get(key, []):
                state = next(iter(raw.get("state", {})), None)
                if state not in ("usable", "qualified"):
                    continue
                interval = raw.get("temporal_interval") or {}
                start = _parse_time(interval.get("start_inclusive"))
                end = _parse_time(interval.get("end_exclusive"))
                if end and end <= now:
                    continue
                if start and start > now + MAX_CERT_LIFETIME:
                    continue
                url = raw.get("monitoring_url") if is_tiled else raw.get("url")
                if not url or not raw.get("log_id"):
                    continue
                logs.append(
                    {
                        "log_id": raw["log_id"],
                        "name": raw.get("description") or url,
                        "operator": operator.get("name", ""),
                        "url": url if url.endswith("/") else url + "/",
                        "is_tiled": is_tiled,
                    }
                )
    return logs


def _parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sync_logs(session):
    # Bring the CTLog table in line with the published log list. If the list
    # can't be fetched, carry on with the logs already known.
    try:
        data = http_get(session, settings.CT_LOG_LIST_URL).json()
        active = parse_log_list(data)
    except (CTError, ValueError) as e:
        logger.warning(f"Unable to fetch the CT log list, using known logs: {e}")
        return
    if not active:
        logger.warning("CT log list has no active logs; keeping known logs")
        return
    for log in active:
        CTLog.objects.update_or_create(
            log_id=log["log_id"],
            defaults={
                "name": log["name"][:255],
                "operator": log["operator"][:255],
                "url": log["url"],
                "is_tiled": log["is_tiled"],
                "is_current": True,
            },
        )
    CTLog.objects.exclude(log_id__in=[log["log_id"] for log in active]).update(
        is_current=False
    )


def select_logs(include=None, exclude=None):
    include = settings.CT_LOG_INCLUDE if include is None else include
    exclude = settings.CT_LOG_EXCLUDE if exclude is None else exclude
    logs = list(CTLog.objects.filter(enabled=True, is_current=True).order_by("name"))
    if include:
        include_re = re.compile(include, re.IGNORECASE)
        logs = [log for log in logs if include_re.search(log.name)]
    if exclude:
        exclude_re = re.compile(exclude, re.IGNORECASE)
        logs = [log for log in logs if not exclude_re.search(log.name)]
    return logs


# --- Log entries ---


def _read_prefixed(buf, offset, size_bytes):
    end = offset + size_bytes
    if end > len(buf):
        raise CTError("truncated entry")
    length = int.from_bytes(buf[offset:end], "big")
    if end + length > len(buf):
        raise CTError("truncated entry")
    return buf[end : end + length], end + length


def read_timestamped_entry(buf, offset):
    # Parses an RFC 6962 TimestampedEntry. Returns (timestamp_ms, is_precert,
    # cert_der, next_offset); cert_der is None for a precert entry, whose
    # parseable precertificate is carried outside this structure.
    if offset + 10 > len(buf):
        raise CTError("truncated entry")
    timestamp, entry_type = struct.unpack_from(">QH", buf, offset)
    offset += 10
    if entry_type == 0:
        cert, offset = _read_prefixed(buf, offset, 3)
        is_precert = False
    elif entry_type == 1:
        # issuer_key_hash, then the TBSCertificate
        _, offset = _read_prefixed(buf, offset + 32, 3)
        cert = None
        is_precert = True
    else:
        raise CTError(f"unknown entry type {entry_type}")
    _, offset = _read_prefixed(buf, offset, 2)  # extensions
    return timestamp, is_precert, cert, offset


def parse_merkle_tree_leaf(leaf_input, extra_data):
    # RFC 6962 get-entries: leaf_input plus extra_data
    if len(leaf_input) < 2 or leaf_input[0] != 0 or leaf_input[1] != 0:
        raise CTError("unsupported leaf version or type")
    timestamp, is_precert, cert, _ = read_timestamped_entry(leaf_input, 2)
    if is_precert:
        # extra_data is a PrecertChainEntry; the precertificate comes first
        cert, _ = _read_prefixed(extra_data, 0, 3)
    return timestamp, is_precert, cert


def read_tile_leaf(buf, offset):
    # static-ct-api TileLeaf
    timestamp, is_precert, cert, offset = read_timestamped_entry(buf, offset)
    if is_precert:
        cert, offset = _read_prefixed(buf, offset, 3)
    _, offset = _read_prefixed(buf, offset, 2)  # chain fingerprints
    return timestamp, is_precert, cert, offset


def tile_path(n):
    # Data tile path per C2SP tlog-tiles: 1234067 -> tile/data/x001/x234/067
    path = f"{n % 1000:03d}"
    n //= 1000
    while n > 0:
        path = f"x{n % 1000:03d}/{path}"
        n //= 1000
    return f"tile/data/{path}"


class TiledLog:
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def size(self):
        lines = http_get(self.session, self.url + "checkpoint").text.split("\n")
        if len(lines) < 2 or not lines[1].isdigit():
            raise CTError("malformed checkpoint")
        return int(lines[1])

    def ranges(self, start, size):
        # Whole tiles only. The partial tile at the tip is read once it fills.
        start -= start % TILE_WIDTH
        end = size - size % TILE_WIDTH
        return [(pos, pos + TILE_WIDTH) for pos in range(start, end, TILE_WIDTH)]

    def fetch(self, start, end):
        # A missing tile means the checkpoint got ahead of the CDN
        tile = http_get(
            self.session,
            self.url + tile_path(start // TILE_WIDTH),
            not_ready=(403, 404),
        ).content
        entries = []
        offset = 0
        for i in range(TILE_WIDTH):
            timestamp, is_precert, cert, offset = read_tile_leaf(tile, offset)
            entries.append((start + i, timestamp, is_precert, cert))
        return entries


class RFC6962Log:
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def size(self):
        sth = http_get(self.session, self.url + "ct/v1/get-sth").json()
        return int(sth["tree_size"])

    def ranges(self, start, size):
        ranges = []
        while start < size:
            end = min((start // RFC6962_BATCH + 1) * RFC6962_BATCH, size)
            ranges.append((start, end))
            start = end
        return ranges

    def fetch(self, start, end):
        entries = []
        # Logs may return fewer entries than asked for
        while start < end:
            url = f"{self.url}ct/v1/get-entries?start={start}&end={end - 1}"
            # Some frontends advertise a tree size ahead of what they serve
            batch = http_get(self.session, url, not_ready=(400,)).json()
            batch = batch.get("entries") or []
            if not batch:
                raise NotReady(f"no entries for {start}-{end - 1}")
            for item in batch[: end - start]:
                timestamp, is_precert, cert = parse_merkle_tree_leaf(
                    base64.b64decode(item["leaf_input"]),
                    base64.b64decode(item["extra_data"]),
                )
                entries.append((start, timestamp, is_precert, cert))
                start += 1
        return entries


def client_for(log, session):
    return (TiledLog if log.is_tiled else RFC6962Log)(log.url, session)


# --- Certificates ---


def normalize_name(name):
    # Returns (hostname, is_wildcard), or None if it isn't a usable hostname
    name = name.strip().lower().rstrip(".")
    is_wildcard = name.startswith("*.")
    if is_wildcard:
        name = name[2:]
    if len(name) > 253 or not HOSTNAME_RE.match(name):
        return None
    return name, is_wildcard


def cert_rows(der, log_name, log_index, timestamp_ms, is_precert):
    # One NewCert field dict per hostname on the certificate
    cert = x509.load_der_x509_certificate(bytes(der))
    names = []
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        names = san.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        pass
    if not names:
        names = [
            f"{attr.value}"
            for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        ]

    common = {
        "issuer": cert.issuer.rfc4514_string()[:255],
        "serial": f"{cert.serial_number:x}"[:64],
        "not_before": cert.not_valid_before_utc,
        "not_after": cert.not_valid_after_utc,
        "is_precert": is_precert,
        "log": log_name[:255],
        "log_index": log_index,
        "logged_at": datetime.fromtimestamp(timestamp_ms / 1000, tz=dt_timezone.utc),
    }
    rows = {}
    for raw in names:
        normalized = normalize_name(raw)
        if not normalized:
            continue
        name, is_wildcard = normalized
        if name not in rows:
            rows[name] = {
                "name": name,
                "tld": name.rsplit(".", 1)[-1],
                "is_wildcard": is_wildcard,
                **common,
            }
    return list(rows.values())


def fetch_rows(client, log_name, start, end):
    # Runs in a worker thread: no database access here.
    # Returns (rows, entry count, unparseable cert count).
    rows = []
    bad = 0
    entries = client.fetch(start, end)
    for index, timestamp, is_precert, der in entries:
        try:
            rows.extend(cert_rows(der, log_name, index, timestamp, is_precert))
        except Exception as e:
            bad += 1
            logger.debug(f"{log_name} entry {index}: {e}")
    return rows, len(entries), bad


def store_rows(rows):
    # Insert the hostnames not already in NewCert. Returns the new names.
    unique = {}
    for row in rows:
        unique.setdefault(row["name"], row)
    names = list(unique)
    created = []
    for i in range(0, len(names), STORE_CHUNK):
        chunk = names[i : i + STORE_CHUNK]
        known = set(
            NewCert.objects.filter(name__in=chunk).values_list("name", flat=True)
        )
        fresh = [name for name in chunk if name not in known]
        NewCert.objects.bulk_create(
            [NewCert(**unique[name]) for name in fresh], ignore_conflicts=True
        )
        created.extend(fresh)
    return created


# --- Ingest ---


class _Job:
    def __init__(self, log, client, ranges):
        self.log = log
        self.client = client
        self.ranges = deque(ranges)
        self.stopped = False


def _log_error(log, error):
    logger.error(f"CT log {log.name}: {error}")
    log.status = "error"
    log.last_error = timezone.now()
    log.error_message = f"{error}"
    log.save()


def ingest_certs(
    max_entries=None, run_seconds=None, include=None, exclude=None, upload=True
):
    # Read the newest entries from every active CT log and store their
    # hostnames. Each log resumes where the last run stopped; if it has grown
    # by more than max_entries since then, the oldest entries are skipped so a
    # run stays bounded. Returns a dict of counts.
    max_entries = max_entries or settings.CT_MAX_ENTRIES_PER_LOG
    run_seconds = run_seconds or settings.CT_MAX_RUN_SECONDS
    deadline = monotonic() + run_seconds
    stats = {
        "logs": 0,
        "entries": 0,
        "new_names": 0,
        "skipped": 0,
        "unparseable": 0,
        "errors": 0,
        "list_key": None,
    }

    session = make_session()
    sync_logs(session)
    logs = select_logs(include, exclude)
    stats["logs"] = len(logs)
    logger.info(f"Reading {len(logs)} CT logs, up to {max_entries} entries each")

    new_names = tempfile.TemporaryFile(mode="w+")
    with ThreadPoolExecutor(max_workers=settings.CT_CONCURRENCY) as pool:
        jobs = []
        clients = [(log, client_for(log, session)) for log in logs]
        sizes = [(log, client, pool.submit(client.size)) for log, client in clients]
        for log, client, future in sizes:
            try:
                size = future.result()
            except Exception as e:
                stats["errors"] += 1
                _log_error(log, e)
                continue
            start = log.position
            if start is None or start > size:
                start = max(size - max_entries, 0)
            elif size - start > max_entries:
                skipped = size - max_entries - start
                log.entries_skipped += skipped
                stats["skipped"] += skipped
                start = size - max_entries
            ranges = client.ranges(start, size)
            log.position = ranges[0][0] if ranges else start
            log.tree_size = size
            log.status = "reading" if ranges else "good"
            log.last_updated = timezone.now()
            log.save()
            if ranges:
                jobs.append(_Job(log, client, ranges))

        while jobs and monotonic() < deadline:
            submitted = []
            for job in jobs:
                for _ in range(min(RANGES_PER_LOG, len(job.ranges))):
                    start, end = job.ranges.popleft()
                    future = pool.submit(
                        fetch_rows, job.client, job.log.name, start, end
                    )
                    submitted.append((job, end, future))
            # Results come back in order per log, so position only moves past
            # entries that were stored.
            for job, end, future in submitted:
                if job.stopped:
                    future.cancel()
                    continue
                try:
                    rows, count, bad = future.result()
                except NotReady as e:
                    logger.info(f"CT log {job.log.name} not ready: {e}")
                    job.stopped = True
                    job.log.status = "good"
                    continue
                except Exception as e:
                    stats["errors"] += 1
                    job.stopped = True
                    _log_error(job.log, e)
                    continue
                created = store_rows(rows)
                for name in created:
                    new_names.write(name + "\n")
                stats["entries"] += count
                stats["unparseable"] += bad
                stats["new_names"] += len(created)
                job.log.position = end
            for job in jobs:
                if not job.ranges and not job.stopped:
                    job.log.status = "good"
                job.log.last_updated = timezone.now()
                job.log.save()
            jobs = [job for job in jobs if job.ranges and not job.stopped]

        for job in jobs:
            # Out of time; the rest is picked up (or skipped) next run
            job.log.status = "behind"
            job.log.save()

    if upload and stats["new_names"] >= int(settings.MIN_DOMAIN_LIST_LENGTH):
        stats["list_key"] = upload_name_list(new_names)
    new_names.close()
    logger.info(f"CT ingest done: {stats}")
    return stats


def upload_name_list(name_file):
    # Write this run's new hostnames to S3, like the new-domain lists
    from Watchman.tools import get_s3_client

    key = f"certs/{timezone.now():%Y%m%d-%H%M%S}.txt"
    try:
        name_file.seek(0)
        get_s3_client().put_object(
            Body=name_file.read(), Bucket=settings.NEWCERT_BUCKET_NAME, Key=key
        )
    except Exception as e:
        logger.error(f"Unable to upload new cert list to S3: {e}")
        return None
    return key

