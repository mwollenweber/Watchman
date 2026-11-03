import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CodeForm, EmailForm
from .models import LoginCode, LoginCodeError

logger = logging.getLogger(__name__)

SESSION_EMAIL = "login_email"
SESSION_NEXT = "login_next"


def _safe_next(request, candidate):
    if candidate and url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return candidate
    return settings.LOGIN_REDIRECT_URL


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def send_login_code(request, email):
    """Issue a code for `email` and send it, unless the address may not sign in.

    An address that can't sign in (deactivated, or unknown while registration
    is closed) gets no email but no error either, so the page can't be used
    to discover which addresses have accounts.
    """
    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if user is not None and not user.is_active:
        logger.info("Login code requested for deactivated account %s", email)
        return
    if user is None and not settings.OPEN_REGISTRATION:
        logger.info("Login code requested for unknown address %s; registration is closed", email)
        return

    login_code, code = LoginCode.issue(email, ip=_client_ip(request))
    context = {
        "code": code,
        "ttl": settings.LOGIN_CODE_TTL_MINUTES,
        "base_url": settings.BASE_URL,
    }
    send_mail(
        subject=f"Your Watchman login code is {code}",
        message=render_to_string("accounts/login_code.txt", context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
    logger.info("Sent login code %s to %s", login_code.pk, email)


@require_http_methods(["GET", "POST"])
def login(request):
    """Step 1: ask for an email address and send it a code.

    This is also registration: an address with no account gets one when its
    first code is verified.
    """
    if request.user.is_authenticated:
        return redirect(_safe_next(request, request.GET.get("next")))

    next_url = request.POST.get("next") or request.GET.get("next") or ""

    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                send_login_code(request, email)
            except LoginCodeError as exc:
                form.add_error("email", str(exc))
            else:
                request.session[SESSION_EMAIL] = email
                request.session[SESSION_NEXT] = next_url
                return redirect("accounts:verify")
    else:
        form = EmailForm(initial={"email": request.session.get(SESSION_EMAIL, "")})

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


@require_http_methods(["GET", "POST"])
def verify(request):
    """Step 2: check the code. On success, sign in, creating the account if new."""
    email = request.session.get(SESSION_EMAIL)
    if not email:
        return redirect("accounts:login")
    if request.user.is_authenticated:
        return redirect(_safe_next(request, request.session.get(SESSION_NEXT)))

    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            try:
                LoginCode.verify(email, form.cleaned_data["code"])
            except LoginCodeError as exc:
                form.add_error("code", str(exc))
            else:
                User = get_user_model()
                user, created = User.objects.get_or_create(
                    email=email, defaults={"user_type": "client"}
                )
                if created:
                    user.set_unusable_password()
                    user.save(update_fields=["password"])
                    logger.info("Registered new user %s", email)
                if not user.is_active:
                    form.add_error(None, "This account has been deactivated.")
                else:
                    auth_login(request, user)
                    next_url = request.session.pop(SESSION_NEXT, "")
                    request.session.pop(SESSION_EMAIL, None)
                    return redirect(_safe_next(request, next_url))
    else:
        form = CodeForm()

    return render(
        request,
        "accounts/verify.html",
        {"form": form, "email": email, "ttl": settings.LOGIN_CODE_TTL_MINUTES},
    )


@require_POST
def resend(request):
    """Send a fresh code to the address from step 1."""
    email = request.session.get(SESSION_EMAIL)
    if not email:
        return redirect("accounts:login")
    try:
        send_login_code(request, email)
    except LoginCodeError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"A new code is on its way to {email}.")
    return redirect("accounts:verify")


@require_http_methods(["GET", "POST"])
def logout(request):
    auth_logout(request)
    return redirect(reverse("accounts:login"))
