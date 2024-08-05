from datetime import datetime, timedelta, timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.html import escape
from django.utils.timezone import make_aware
from django.template import loader
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth import login as auth_login
from django.views.decorators.http import require_http_methods
from Watchman.models import Domain, ZoneList, Match, ClientUser


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


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect(index)

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(index)
    else:
        form = UserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'signup.html', context)


@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect(index)

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or index)
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


@permission_required('is_superuser')
def zone_status(request):
    zone_list = ZoneList.objects.filter(enabled=True).all()
    if request.method == 'GET':
        # if request.content_type == 'application/json':
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
                    # 'error_message': zone.error_messsage,
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


#todo associate user wiht a client and filter
@login_required()
def hits(request):
    myuser = ClientUser.objects.filter(user=request.user,
                                    #is_active=True
    ).first()
    if not myuser:
        return JsonResponse({
            'status': 'error',
        })

    if request.user.is_superuser:
        hit_list = Match.objects.all()
    else:
        hit_list = Match.objects.filter(client=myuser.client).all()

    if request.method == 'GET':
        # if request.content_type == 'application/json':
        if 1 == 1:
            ret_list = []
            for hit in hit_list:
                ret_list.append({
                    'name': hit.hit,
                    'created': hit.created,
                    'modified': hit.last_modified,
                    'is_new': hit.is_new,
                    'is_reviewed': hit.is_reviewed,
                    'is_fp': hit.is_fp,
                    'client': hit.client.name,
                })
            ret = {
                'status': 'success',
                'count': len(ret_list),
                'hits': ret_list
            }
            return JsonResponse(ret)
        else:
            return HttpResponse(status=200)

    elif request.method == 'POST':
        return HttpResponse("")
