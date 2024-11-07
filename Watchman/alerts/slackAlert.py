import logging
from slack import WebClient
from slack_sdk.webhook import WebhookClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)


def sendSlackMessage(apitoken: str, channel: str, message: str) -> None:
    try:
        logger.debug(f"Sending Slack message: {message}")
        client = WebClient(apitoken)
        response = client.chat_postMessage(channel=channel, text=f"{message}")
        logger.debug(f"Response: {response}")
    except SlackApiError as e:
        logger.error(f"{e} {response}")


def sendSlackWebhook(url: str, message: str) -> None:
    logger.debug(f"Sending SlackWebook message: {message}")
    webhook = WebhookClient(url)
    response = webhook.send(text=message)
    assert response.status_code == 200
    assert response.body == "ok"
