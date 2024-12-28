import requests


class VTEnrichment:
    def __init__(self, api_key, timmeout=5):
        self.base_url = 'https://www.virustotal.com/api/v3'
        self.timeout = timmeout
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'x-apikey': self.api_key,
        }


    def lookup_domain(self, domain):
        url = f'{self.base_url}/domains/{domain}'
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

