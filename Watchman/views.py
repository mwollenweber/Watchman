from datetime import datetime, timedelta, timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.html import escape
from django.utils.timezone import make_aware
from django.template import loader
from django.conf import settings
from Watchman.forms import LoginForm
from Watchman.models import Domain, ZoneList


def current_datetime(request):
    now = datetime.utcnow()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required()
def zone_status(request):
    zone_list = ZoneList.objects.filter(enabled=True).all()
    if request.method == 'GET':
        #if request.content_type == 'application/json':
        if 1 == 1:
            ret_list = []
            for zone in zone_list:
                ret_list.append({
                    'name': zone.name,
                    'status': zone.status,
                    'enabled': zone.enabled,
                    'update_interval': zone.update_interval,
                    'last_updated': zone.last_updated,
                    'last_completed': zone.last_completed,
                    'last_diffed': zone.last_diffed,
                    'last_error': zone.last_error,
                    #'error_message': zone.error_messsage,
                })
            ret = {
                'status': 'success',
                'count': len(ret_list),
                'zones': ret_list
            }
            return JsonResponse(ret)
        else:
            return HttpResponse(status=200)

    elif request.method == 'POST':
        return HttpResponse("")


def index(request):
    if request.method == 'GET':
        template = loader.get_template('base.html')
        context = {
        }
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        return HttpResponse("POST")
