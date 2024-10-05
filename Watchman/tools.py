import re
import logging
import glob
import os
import dns.resolver
import socket
from time import time
from django.db import IntegrityError
from django.conf import settings
from Levenshtein import distance
from django.utils import timezone
from datetime import timedelta, datetime
from Watchman.models import Domain, NewDomain, Match, Search, ClientAlert
from Watchman.alerts.slackAlert import sendSlackMessage
from Watchman.alerts.email import send_email
from Watchman.settings import BASE_URL

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 11000000000


def has_mx(domain):
    try:
        ans = dns.resolver.resolve(domain, "MX")
        logger.info(f"mx found! for {domain}")
        return True
    except dns.resolver.NXDOMAIN:
        logger.warn("mx not found")
    return False


def has_ip(fqdn):
    try:
        ans = dns.resolver.resolve(fqdn)
        return True
    except dns.resolver.NXDOMAIN as e:
        logger.error(e)
    return False


def get_ip_list(fqdn):
    try:
        ans = dns.resolver.resolve(fqdn)
        return ans.rrset
    except dns.resolver.NXDOMAIN as e:
        logger.error(e)

    return None


def clean_temp():
    files = glob.glob(f"{settings.TEMP_DIR}/*txt")
    current_time = time()

    for f in files:
        time_delta_days = (current_time - os.path.getmtime(f)) / (60 * 60 * 24)
        if time_delta_days > settings.MAX_TEMP_AGE:
            logger.info(f"deleting: {f}")
            os.remove(f)


def expire_new():
    threshold = timezone.now() - timedelta(days=settings.MAX_NEW_AGE)
    old = NewDomain.objects.filter(created__lt=threshold, is_expired=False)
    for m in old.iterator():
        try:
            logger.info(f"{m.domain} {m.created}")
            m.is_expired = True
            m.save()
        except Exception as e:
            logger.error(e)


def diff_zone(zone):
    logger.info(f"diffing zone {zone}")
    try:
        zone.status = "diffing"
        zone.last_updated = timezone.now()
        zone.save()

        oldfile, newfile = getZonefiles(zone.name)
        old = open(oldfile, "r")
        new = open(newfile, "r")
        domain_list = diff_files(old, new)
        load_diff(domain_list)

        zone.status = "good"
        now = timezone.now()
        zone.last_updated = now
        zone.last_completed = now
        zone.last_diffed = now
        zone.save()
        logger.info(f"DONE zone={zone.name}")

    except FileNotFoundError as e:
        logger.error(e)
        zone.last_error = timezone.now()
        zone.error_message = f"{e}"
        zone.status = "error"
        zone.save()
        return

    except Exception as e:
        logger.error(e)
        zone.last_error = timezone.now()
        zone.error_message = f"{e}"
        zone.status = "error"
        zone.save()


def run_search(method, criteria, target_list, tolerance=None):
    logger.info(f"running search: {method} {criteria}")

    if f"{method}" == "substring":
        logging.debug("trying substring")
        match = MatchSubString(criteria)
    elif f"{method}" == "regex":
        logging.debug("trying regex")
        match = MatchRegEx(criteria)
    elif f"{method}" == "strdistance":
        logging.debug("trying strdistance")
        match = MatchEditDistance(criteria, tolerance=tolerance)
    else:
        logging.error(f"No match for {method}")
        return

    return match.run(target_list)


def run_searches():
    logging.info("Running Searches")

    # run the new domain as target list first
    logger.info("Running newdomain searches")
    target_list = NewDomain.objects.filter(is_expired=False).values_list(
        "domain", flat=True
    )
    search_list = Search.objects.filter(is_active=True, database="newdomains")
    for s in search_list:
        if s.last_completed < timezone.now() - timedelta(seconds=s.update_interval):
            if s.last_updated < timezone.now() - timedelta(
                seconds=settings.MIN_UPDATE_INTERVAL
            ):
                logger.info(f"{s} on {len(target_list)} domains")
                # todo = update status timestamps
                hits = (
                    run_search(s.method, s.criteria, target_list, tolerance=s.tolerance)
                    or []
                )
                for h in hits:
                    try:
                        Match.objects.get_or_create(
                            hit=h,
                            client=s.client,
                            defaults={
                                "last_modified": timezone.now(),
                            },
                        )
                    except Exception as e:
                        logger.error(e)

    # run searches on all domains a
    logger.info("Running full domain searches")
    target_list = Domain.objects.all().values_list("domain", flat=True)
    search_list = Search.objects.filter(is_active=True, database="domains")
    for s in search_list:
        if s.last_completed < timezone.now() - timedelta(seconds=s.update_interval):
            if s.last_updated < timezone.now() - timedelta(
                seconds=settings.MIN_UPDATE_INTERVAL
            ):
                logger.info(f"{s} on {len(target_list)} domains")
                # todo = update status timestamps
                hits = (
                    run_search(s.method, s.criteria, target_list, tolerance=s.tolerance)
                    or []
                )
                for h in hits:
                    try:
                        Match.objects.get_or_create(
                            hit=h,
                            client=s.client,
                            defaults={
                                "last_modified": timezone.now(),
                            },
                        )
                    except Exception as e:
                        logger.error(e)


def load_diff(domain_list):
    for domain in domain_list:
        try:
            name, tld = domain.split(".")
            if settings.MAINTAIN_FULL_ZONEFILES:
                d = Domain.objects.create(
                    domain=domain,
                    tld=tld,
                    is_new=True,
                )
                d.save()
            NewDomain.objects.create(domain=domain, tld=tld)
        except ValueError as e:
            continue

        except IntegrityError as e:
            # logging.debug(e, exc_info=True)
            continue


def getZonefiles(zone):
    logger.info("Getting zone files for %s", zone)
    modified_files = glob.glob(f"{settings.TEMP_DIR}/*-{zone}.txt")
    modified_files.sort(key=lambda x: os.path.getmtime(x))
    logger.info(f"DIFFING: {modified_files[-2]} {modified_files[-1]}")
    return modified_files[-2], modified_files[-1]


def diff_lists(oldlist, newlist):
    return list(set(newlist) - set(oldlist))


def memory_diff_files(old_file, new_file):
    try:
        old = old_file.read().split()
        new = new_file.read().split()
        return diff_lists(old, new)
    except IOError as e:
        logging.error(e, exc_info=True)


def diff_files(old_file, new_file):
    count = 0
    new_list = []
    old = old_file.readline().strip()
    new = new_file.readline().strip()

    while len(old) > 0:
        if old == new:
            old = old_file.readline().strip()
            new = new_file.readline().strip()
        elif new < old:
            new_list.append(new)
            new = new_file.readline().strip()
        else:
            old = old_file.readline().strip()

        count += 1
        if count > MAX_ITERATIONS:
            logging.warn("MAX ITERATIONS HIT. Quitting")
            break

        if len(new) < 1:
            break

    new_list.append(new)
    for line in new_file:
        new_list.append(line.strip())

    return new_list


class MatchMethod:
    def __init__(self, criteria):
        self.name = None
        self.criteria = None

    def run(self, target_list):
        raise NotImplementedError("Must override method")

    def update_matches(self, hit_list):
        logger.info("hitlist")


# this is a stupid way for substring...
class MatchSubString(MatchMethod):
    def __init__(self, criteria):
        self.name = "substring"
        self.criteria = criteria.lower()

    def run(self, target_list):
        hit_list = []
        for target in target_list:
            if self.criteria in target:
                hit_list.append(target)
        return hit_list


class MatchRegEx(MatchMethod):
    def __init__(self, criteria):
        self.name = "regex"
        self.criteria = criteria
        self.regex = re.compile(criteria, re.IGNORECASE)

    def run(self, target_list):
        hit_list = []
        for target in target_list:
            m = self.regex.match(target)
            if m:
                hit_list.append(target)

        return hit_list


class MatchEditDistance(MatchMethod):
    def __init__(self, criteria, tolerance=42):
        self.name = "edit_distance"
        self.criteria = criteria
        self.tolerance = tolerance

    def run(self, target_list):
        hit_list = []
        for target in target_list:
            if distance(target, self.criteria) < self.tolerance:
                hit_list.append(target)

        return hit_list


def run_alerts():
    for m in Match.objects.filter(has_alerted=False).filter(is_fp=False).all():
        has_error = False
        alerts = ClientAlert.objects.filter(client=m.client).filter(enabled=True).all()
        for a in alerts:
            now = datetime.utcnow().isoformat()
            config = a.config
            message = f"[WATCHMAN ALERT] {now} : Match Detected on {m.hit} for more information {BASE_URL}/alert/?id={a.id}"
            if a.alert_type == "slack":
                logger.info("alert type = slack")
                sendSlackMessage(config["apikey"], config["channel"], message)
            elif a.alert_type == "gmail":
                logger.info("fixme: alert type = gmail")
            elif a.alert_type == "email":
                logger.info("alert type = email")
                config = a.config
                send_email(config, message)
            elif a.alert_type == "s3":
                logger.info("fixme: alert type = s3")
            else:
                logger.error("Unhandled alert type: {a.alert_type}")
                has_error = True

        if not has_error:
            m.has_alerted = True
            m.save()
