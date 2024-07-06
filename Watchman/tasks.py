from django.conf import settings
from .celery import app


@app.task(name="test")
def test():
    print("This is a test")
