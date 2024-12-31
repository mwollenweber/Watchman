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
from Watchman.tools import has_mx, has_website
from Watchman.enrichments.vt import VT

logger = logging.getLogger(__name__)


def current_datetime(request):
    now = datetime.utcnow()
    return JsonResponse({"status": "ok", "now": f"{now.isoformat()}"})


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


@login_required()
@require_http_methods(["GET"])
def is_nod(request):
    value = request.GET.get("value", "example.com")
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


@login_required()
@require_http_methods(["GET"])
def search(request):
    required_params = ["value", "type"]
    ret = {
        "status": "error",
    }

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

    ret = {
        "status": "success",
        "count": len(results),
        "results": results,
    }
    return JsonResponse(ret)


@require_http_methods(["GET"])
@login_required()
def hits(request):
    event_id = request.GET.get("id", None)
    enrich = request.GET.get("enrich", False)
    if request.user.is_superuser:
        if event_id:
            hit_list = Match.objects.filter(id=event_id)
        else:
            hit_list = Match.objects.all()
    else:
        myuser = ClientUser.objects.filter(user=request.user).first()
        if event_id:
            hit_list = Match.objects.filter(id=event_id, client=myuser.client).all()
        else:
            hit_list = Match.objects.filter(client=myuser.client).all()

    ret_list = []
    for hit in hit_list:
        if enrich: vt_data = VT().lookup_domain(hit.hit)
        ret = {
            "name": hit.hit,
            "id": hit.id,
            "created": hit.created,
            "modified": hit.last_modified,
            "is_new": hit.is_new,
            "is_reviewed": hit.is_reviewed,
            "is_fp": hit.is_fp,
            "client": hit.client.name,
            #fixme this is slow
            # "has_mx": has_mx(hit.hit),
            # "has_website": has_website(hit.hit),
        }
        if enrich:
            vt_data = VT().lookup_domain(hit.hit)
            ret["enrichments"] = {
                "virustotal": vt_data,
            }
        ret_list.append(ret)
    return JsonResponse({"status": "success", "count": len(ret_list), "hits": ret_list})


@require_http_methods(["GET"])
@login_required()
def view_alerts(request):
    # request.user
    # alert_id
    return JsonResponse(status=200)
