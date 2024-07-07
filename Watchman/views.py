import traceback
from datetime import datetime, timedelta, timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.timezone import make_aware
from django.template import loader
from django.conf import settings
from Watchman.models import Domain


def current_datetime(request):
    now = datetime.utcnow()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def index(request):
    if request.method == 'GET':
        template = loader.get_template('base.html')
        context = {
        }
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        return HttpResponse("POST")
