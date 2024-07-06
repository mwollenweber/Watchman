import logging
import sys
import requests
import traceback
from datetime import datetime


def ingest_zonefile(zone_file):
    domain_list = []
    for line in zone_file:
        try:
            # domain_list.append(line.lower().strip().split()[0])
            domain_list.append(line.lower().strip().split()[0][:-1])
        except IndexError:
            traceback.print_exc()

    return domain_list


def compare_sorted_files(file1, file2):
    count = 0
    for line in file1:
        l1 = line.lower().strip()
        l2 = file2.readline().lower().strip()
        if l1 == l2:
            count += 1
        else:
            print(f"{count}: {l1} != {l2}")
            break

class czds:
    def __init__(self):
        print("init")
        self.username = ''
        self.password = ''
        self.auth_base_url = 'https://account-api.icann.org'
        self.base_url = 'https://czds-api.icann.org'



if __name__ == "__main__":
    print(datetime.utcnow())
    # filename = sys.argv[1]
    # zone_file = open(filename, 'r')
    # outfile = open('./out.txt', 'w')
    # domain_list = ingest_zonefile(zone_file)
    # domain_list.sort()
    #
    # for line in domain_list:
    #     outfile.write(f"{line}\n")


    # file1 = open('./out.txt', 'r')
    # file2 = open('/Users/mjw/projects/icann/out.txt', 'r')
    # compare_sorted_files(file1, file2)

    print(datetime.utcnow())
