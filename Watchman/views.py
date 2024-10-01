import logging
from datetime import datetime, timedelta, timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, logout  # , login
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
from Watchman.models import Domain, ZoneList, Match, ClientUser, NewDomain

logger = logging.getLogger(__name__)


def current_datetime(request):
    now = datetime.utcnow()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


@require_http_methods(["GET"])
def index(request):
    if request.content_type == "application/json":
        return JsonResponse({"status": "ok"})
    else:
        template = loader.get_template("base.html")
        context = {}
        return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    return redirect("index")


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect(index)

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(index)
    else:
        form = UserCreationForm()
    context = {
        "form": form,
    }
    return render(request, "signup.html", context)


@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated:
        return redirect(index)

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get("next") or index)
    else:
        form = AuthenticationForm()
    context = {
        "form": form,
    }
    return render(request, "login.html", context)


@permission_required("is_superuser")
def zone_status(request):
    zone_list = ZoneList.objects.filter(enabled=True).all()
    if request.method == "GET":
        # if request.content_type == 'application/json':
        if 1 == 1:
            ret_list = []
            for zone in zone_list:
                ret_list.append(
                    {
                        "name": zone.name,
                        "status": zone.status,
                        "enabled": zone.enabled,
                        "update_interval": zone.update_interval,
                        "last_updated": zone.last_updated,
                        "last_completed": zone.last_completed,
                        "last_diffed": zone.last_diffed,
                        "last_error": zone.last_error,
                        # 'error_message': zone.error_messsage,
                    }
                )
            ret = {"status": "success", "count": len(ret_list), "zones": ret_list}
            return JsonResponse(ret)
        else:
            return HttpResponse(status=200)

    elif request.method == "POST":
        return HttpResponse("")


@login_required()
@require_http_methods(["GET"])
def is_nod(request):
    # if request.content_type == 'application/json':
    if 1 == 1:
        value = request.GET.get("value", None)
        data = NewDomain.objects.filter(domain__icontains=value).first()
        if data:
            return JsonResponse(
                {
                    "status": "success",
                    "found": True,
                    "is_nod": True,
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "success",
                    "found": False,
                    "is_nod": False,
                }
            )

    return JsonResponse({"status": "error"})


@login_required()
@require_http_methods(["GET"])
def search(request):
    required_params = ["value", "type"]
    ret = {
        "status": "error",
    }
    # if request.content_type == 'application/json':
    if 1 == 1:
        value = request.GET.get("value", None)
        search_type = request.GET.get("search_type", None)
        results = []

        if search_type == "new_domain":
            data = NewDomain.objects.filter(domain__icontains=value).all()
            for d in data:
                results.append(d.to_dict())
        elif search_type == "domain":
            data = Domain.objects.filter(domain__icontains=value).all()
            for d in data:
                results.append(d.to_dict())
        elif search_type == "nod":
            return is_nod(request)
        elif search_type == "fqdn":
            logger.warn("search type fqdn todo")

        return JsonResponse(
            {
                "status": "success",
                "search_type": search_type,
                "results": results,
                "count": len(results),
            }
        )

    return JsonResponse(ret)


@require_http_methods(["GET"])
def new_domains(request):
    results = []
    for domain in NewDomain.objects.filter(is_expired=False).order_by("created"):
        results.append(
            {
                "domain": f"{domain.domain}",
                "created": f"{domain.created}",
                "tld": f"{domain.tld}",
            }
        )

    # if request.content_type == 'application/json':
    if 1 == 1:
        ret = {
            "status": "success",
            "count": len(results),
            "results": results,
        }
        return JsonResponse(ret)


@login_required()
def hits(request):
    if request.user.is_superuser:
        hit_list = Match.objects.all()
    else:
        myuser = ClientUser.objects.filter(user=request.user).first()
        hit_list = Match.objects.filter(client=myuser.client).all()
        if not myuser:
            return JsonResponse(
                {
                    "status": "error",
                }
            )

    if request.method == "GET":
        # if request.content_type == 'application/json':
        if 1 == 1:
            ret_list = []
            for hit in hit_list:
                ret_list.append(
                    {
                        "name": hit.hit,
                        "created": hit.created,
                        "modified": hit.last_modified,
                        "is_new": hit.is_new,
                        "is_reviewed": hit.is_reviewed,
                        "is_fp": hit.is_fp,
                        "client": hit.client.name,
                    }
                )
            ret = {"status": "success", "count": len(ret_list), "hits": ret_list}
            return JsonResponse(ret)
    return JsonResponse(status=200)


@require_http_methods(["GET"])
@login_required()
def view_alerts(request):
    # request.user
    # alert_id
    return JsonResponse(status=200)
