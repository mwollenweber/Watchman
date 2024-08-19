import logging
from django.conf import settings
from slack import WebClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)

client = WebClient(token=settings.SLACK_TOKEN)


def test(message=""):
    try:
        logger.info("Testing slack")
        response = client.chat_postMessage(channel=settings.SLACK_CHANNEL, text=f"{message}")
    except SlackApiError as e:
        print(f"{e}")
