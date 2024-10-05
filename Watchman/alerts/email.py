import smtplib
import logging
from email.message import EmailMessage


logger = logging.getLogger(__name__)


def send_email(config, message):
    logger.info("Email Message!!")
    recipient = config.get("recipient")
    sender = config.get("sender")
    password = config.get("password")
    servername = config.get("server")

    msg = EmailMessage()
    msg.set_content(message)

    msg["Subject"] = config.get("subject")
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL(servername, 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
