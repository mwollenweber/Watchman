import logging
import io
import sys
import requests
import traceback
import json
import cgi
import gzip
from Watchman.models import Domain
from datetime import datetime
from django.conf import settings
from datetime import datetime


def ingest_zonefile(zone_file):
    domain_list = []
    for line in zone_file:
        try:
            domain = line.lower().strip().split()[0][:-1].decode('ascii')
            domain_list.append(domain)
        except IndexError:
            traceback.print_exc()

    domain_list.sort()
    return domain_list


class CZDS:
    def __init__(self, username=None, password=None):
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
        auth_url = self.auth_base_url + '/api/authenticate'
        auth_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        credential = {
            'username': self.username,
            'password': self.password,
        }

        response = requests.post(auth_url, data=json.dumps(credential), headers=auth_headers)
        status_code = response.status_code

        # Return the access_token on status code 200. Otherwise, terminate the program.
        if status_code == 200:
            access_token = response.json()['accessToken']
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
            print(f'{len(zone_links)} zones downloaded')
            return zone_links
        elif status_code == 401:
            print("The access_token has been expired. Re-authenticate")
            self.is_authenticated = False
            access_token = self.authenticate()
            self.get_zone_links()
        else:
            sys.stderr.write("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))
            return None

    def download_one_zone(self, url):
        print("{0}: Downloading zone file from {1}".format(str(datetime.now()), url))
        if not self.is_authenticated:
            self.authenticate()

        download_zone_response = requests.get(url, headers=self.headers, stream=True)
        status_code = download_zone_response.status_code
        if status_code == 200:
            # Try to get the filename from the header
            _, option = cgi.parse_header(download_zone_response.headers['content-disposition'])
            filename = option.get('filename')

            # If could get a filename from the header, then makeup one like [tld].txt.gz
            if not filename:
                filename = url.rsplit('/', 1)[-1].rsplit('.')[-2] + '.txt.gz'

            f = io.BytesIO()
            for chunk in download_zone_response.iter_content(1024):
                f.write(chunk)
            print(f"Completed downloading {filename}")

        elif status_code == 401:
            print("The access_token has been expired")
            self.is_authenticated = False
        elif status_code == 404:
            print("No zone file found for {0}".format(url))
        else:
            sys.stderr.write('Failed to download zone from {0} with code {1}\n'.format(url, status_code))

        data = io.BytesIO(gzip.decompress(f.getbuffer()))
        domain_list = ingest_zonefile(data)
        return domain_list

    def load_zonefile(self, zone):
        if not self.is_authenticated:
            self.authenticate()

        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
        for domain in myicann.download_one_zone(link):
            try:
                name, tld = domain.split('.')
                obj, created = Domain.objects.update_or_create(
                    domain=domain,
                    tld=tld,
                )
            except ValueError as e:
                print(f"ERROR: domain={domain}")
                # traceback.print_exc()
