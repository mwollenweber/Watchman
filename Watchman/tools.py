import glob
import Levenshtein
import os
import re
import logging
from time import time
from django.db import IntegrityError
from django.conf import settings
from Watchman.models import Domain, NewDomain

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 11000000000


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


def load_diff(domain_list):
    for domain in domain_list:
        try:
            name, tld = domain.split('.')
            d = Domain.objects.create(
                domain=domain,
                tld=tld,
                is_new=True,
            )
            NewDomain.objects.create(
                domain=domain,
                tld=tld
            )
        except ValueError as e:
            continue

        except IntegrityError as e:
            # logging.debug(e, exc_info=True)
            continue


def getZonefiles(zone):
    logger.info("Getting zone files for %s", zone)
    files = glob.glob(f"{settings.TEMP_DIR}/*-{zone}.txt")
    modified_files = list()
    current_time = time()

    for zonefile in files:
        time_delta = current_time - os.path.getmtime(zonefile)
        time_delta_days = time_delta / (60 * 60 * 24)
        if time_delta_days < 4:
            modified_files.append(zonefile)

    modified_files.sort(key=lambda x: os.path.getmtime(x))
    logger.debug(f"DIFFING: {modified_files[0]} {modified_files[-1]}")
    return modified_files[0], modified_files[-1]


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

    def run(self, target_list):
        hit_list = []

        return hit_list


class MatchEditDistance(MatchMethod):
    def __init__(self, criteria, tolerance=42):
        self.name = "edit_distance"
        self.criteria = criteria
        self.distance = tolerance

    def run(self, target_list):
        hit_list = []

        return hit_list
