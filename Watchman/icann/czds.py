import logging
import io
import sys
import requests
import json
import cgi
import gzip
from Watchman.models import Domain
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def zonefile2list(zone_file):
    logger.debug("zonefile2list")
    domain_set = set()
    for line in zone_file:
        try:
            domain_set.add(line.decode("ascii").split()[0][:-1].lower().strip())
        except IndexError as e:
            logger.error(e)

    zone_file.close()
    domain_list = list(domain_set)
    del domain_set

    logger.debug("Sorting")
    domain_list.sort()
    logger.debug("zonefile2list done")
    return domain_list


def update_zonefile(zone):
    count = 0
    myicann = CZDS()
    myicann.authenticate()
    logger.info("Downloading")
    link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
    filename = f"{settings.TEMP_DIR}/{timezone.now():%Y%m%d}-{zone}.txt"

    zone_list = myicann.download_one_zone(link)
    outfile = open(filename, "w")
    for line in zone_list:
        outfile.write(f"{line}\n")
        count += 1
        if count % 10000 == 0:
            logger.debug(f"{count} domains written to {filename}")


class CZDS:
    def __init__(self, username=None, password=None):
        self.username = username or settings.ICANN_USERNAME
        self.password = password or settings.ICANN_PASSWORD
        self.auth_base_url = "https://account-api.icann.org"
        self.base_url = "https://czds-api.icann.org"
        self.access_token = None
        self.is_authenticated = False
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def authenticate(self):
        auth_url = self.auth_base_url + "/api/authenticate"
        auth_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        credential = {
            "username": self.username,
            "password": self.password,
        }

        response = requests.post(
            auth_url, data=json.dumps(credential), headers=auth_headers
        )
        status_code = response.status_code

        # Return the access_token on status code 200. Otherwise, terminate the program.
        if status_code == 200:
            access_token = response.json()["accessToken"]
            self.headers["Authorization"] = "Bearer {0}".format(access_token)
            self.is_authenticated = True
            self.access_token = access_token
            return access_token
        elif status_code == 404:
            logger.error("Invalid url " + auth_url)
        elif status_code == 401:
            logger.error(
                "Invalid username/password. Please reset your password via web"
            )
        elif status_code == 500:
            logger.error("Internal server error. Please try again later")
        else:
            logger.error(
                "Failed to authenticate with error code {0}".format(status_code)
            )
            logger.error(response.text)

    def get_zone_links(self):
        links_url = self.base_url + "/czds/downloads/links"
        links_response = requests.get(links_url, headers=self.headers, stream=True)
        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            logger.debug(f"{len(zone_links)} zones downloaded")
            return zone_links
        elif status_code == 401:
            logger.debug("The access_token has been expired. Re-authenticate")
            self.is_authenticated = False
            access_token = self.authenticate()
            self.get_zone_links()
        else:
            logger.error(
                "Failed to get zone links from {0} with error code {1}\n".format(
                    links_url, status_code
                )
            )
            return None

    def download_one_zone(self, url):
        logger.debug(
            "{0}: Downloading zone file from {1}".format(str(timezone.now()), url)
        )
        if not self.is_authenticated:
            self.authenticate()

        download_zone_response = requests.get(url, headers=self.headers, stream=True)
        status_code = download_zone_response.status_code
        if status_code == 200:
            # Try to get the filename from the header
            _, option = cgi.parse_header(
                download_zone_response.headers["content-disposition"]
            )
            filename = option.get("filename")

            # If could get a filename from the header, then makeup one like [tld].txt.gz
            if not filename:
                filename = url.rsplit("/", 1)[-1].rsplit(".")[-2] + ".txt.gz"

            f = io.BytesIO()
            for chunk in download_zone_response.iter_content(1024):
                f.write(chunk)
            logger.debug(f"Completed downloading {filename}")

        elif status_code == 401:
            logger.error("The access_token has been expired")
            self.is_authenticated = False
        elif status_code == 404:
            logger.error("No zone file found for {0}".format(url))
        else:
            logger.error(
                "Failed to download zone from {0} with code {1}\n".format(
                    url, status_code
                )
            )

        logger.info(f"Done downloading {url}")
        logger.debug("Decompressing zonefile")
        data = io.BytesIO(gzip.decompress(f.getbuffer()))
        return zonefile2list(data)

    def load_zonefile(self, zone):
        if not self.is_authenticated:
            self.authenticate()

        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
        for domain in self.download_one_zone(link):
            try:
                name, tld = domain.split(".")
                d = Domain.objects.create(domain=domain, tld=tld, is_new=True)
            except ValueError as e:
                # logger.debug(f"ERROR: domain={domain}")
                continue
            except IntegrityError as e:
                continue
