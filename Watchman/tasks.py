import logging
from django.conf import settings
from .celery import app

logger = logging.getLogger(__name__)


@app.task(name="test")
def test():
    logger.debug("This is a test")
