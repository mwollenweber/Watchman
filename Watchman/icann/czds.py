import logging
import sys
import requests
import traceback
import json
from datetime import datetime
from django.conf import settings


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
    def __init__(self, username=None, password=None):
        print("init")
        self.username = username or settings.ICANN_USERNAME
        self.password = password or settings.ICANN_PASSWORD
        self.auth_base_url = 'https://account-api.icann.org'
        self.base_url = 'https://czds-api.icann.org'
        self.access_token = None
        self.is_authenticated = False
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def authenticate(self):
        print("authenticate")
        auth_headers =  {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        credential = {
            'username': self.username,
            'password': self.password,
        }

        auth_url = self.auth_base_url + '/api/authenticate'
        response = requests.post(auth_url, data=json.dumps(credential), headers=auth_headers)
        status_code = response.status_code

        # Return the access_token on status code 200. Otherwise, terminate the program.
        if status_code == 200:
            access_token = response.json()['accessToken']
            print('{0}: Received access_token:'.format(datetime.datetime.now()))
            print(access_token)
            self.headers['Authorization'] = 'Bearer {0}'.format(access_token)
            self.is_authenticated = True
            self.access_token = access_token
            return access_token
        elif status_code == 404:
            sys.stderr.write("Invalid url " + auth_url)
        elif status_code == 401:
            sys.stderr.write("Invalid username/password. Please reset your password via web")
        elif status_code == 500:
            sys.stderr.write("Internal server error. Please try again later")
        else:
            sys.stderr.write("Failed to authenticate user {0} with error code {1}".format(username, status_code))

    def get_zone_links(self):
        links_url = self.base_url + "/czds/downloads/links"
        links_response = requests.get(links_url, headers=self.headers, stream=True)
        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            print("{0}: The number of zone files to be downloaded is {1}".format(datetime.datetime.now(), len(zone_links)))
            return zone_links
        elif status_code == 401:
            print("The access_token has been expired. Re-authenticate")
            self.is_authenticated = False
            access_token = self.authenticate()
            self.get_zone_links()
        else:
            sys.stderr.write("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))
            return None


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
