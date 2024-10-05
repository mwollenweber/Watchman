import logging
from slack import WebClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)


def sendSlackMessage(apitoken: str, channel: str, message: str) -> None:
    try:
        logger.debug(f"Sending Slack message: {message}")
        client = WebClient(apitoken)
        response = client.chat_postMessage(channel=channel, text=f"{message}")
        logger.debug(f"Response: {response}")
    except SlackApiError as e:
        print(f"{e} {response}")
        return
