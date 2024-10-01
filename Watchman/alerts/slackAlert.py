import logging
from slack import WebClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)


def sendSlackMessage(apitoken: str, channel: str, message: str) -> bool:
    try:
        logger.info("Testing slack")
        client = WebClient(apitoken)
        response = client.chat_postMessage(channel=channel, text=f"{message}")
    except SlackApiError as e:
        print(f"{e}")
        return False

    return True
