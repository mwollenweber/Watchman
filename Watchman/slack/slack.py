import logging
from slack_sdk import WebClient


logger = logging.getLogger(__name__)

def test():
    client = WebClient()
    api_response = client.api_test()