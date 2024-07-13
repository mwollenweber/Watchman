import glob
import Levenshtein
import os
import traceback
from time import time
from django.db import IntegrityError
from django.conf import settings
from Watchman.models import Domains, NewDomains

MAX_ITERATIONS = 11000000000


def load_diff(domain_list):
    for domain in domain_list:
        try:
            name, tld = domain.split('.')
            d = Domains.objects.create(
                domain=domain,
                tld=tld,
                is_new=True,
            )
            NewDomains.objects.create(
                domain=domain,
                tld=tld,
            )
        except ValueError as e:
            # print(f"ERROR: domain={domain}")
            # traceback.print_exc()
            continue

        except IntegrityError as e:
            traceback.print_exc()
            continue


def getZonefiles(zone):
    files = glob.glob(f"{settings.TEMP_DIR}/*-{zone}.txt")
    modified_files = list()
    current_time = time()

    for zonefile in files:
        time_delta = current_time - os.path.getmtime(zonefile)
        time_delta_days = time_delta / (60 * 60 * 24) * 7
        if time_delta_days < 60:
            modified_files.append(zonefile)

    modified_files.sort(key=lambda x: os.path.getmtime(x))
    return modified_files[-2], modified_files[-1]


def diff_lists(oldlist, newlist):
    return list(set(newlist) - set(oldlist))


def memory_diff_files(old_file, new_file):
    try:
        old = old_file.read().split()
        new = new_file.read().split()
        return diff_lists(old, new)
    except IOError:
        traceback.print_exc()


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
            print("MAX ITERATIONS HIT. Quitting")
            break

        if len(new) < 1:
            break

        # if count % 100000 == 0:
        #     print(f"count={count}")

    new_list.append(new)
    for line in new_file:
        new_list.append(line.strip())

    return new_list
