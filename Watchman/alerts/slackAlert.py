import logging
from slack import WebClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)

slack_token = "xoxb-7115007943571-7532238629330-7a56QdoTB0KffoPb3YuhmTrd"
client = WebClient(token=slack_token)


def test(message=""):
    try:
        logger.info("Testing slack")
        response = client.chat_postMessage(channel="C07FFDYD430", text=f"{message}")
    except SlackApiError as e:
        print(f"{e}")
