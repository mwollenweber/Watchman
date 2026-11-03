import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import LoginCode, LoginCodeError

User = get_user_model()

CODE_RE = re.compile(r"\b(\d{6})\b")


def code_from_email(message):
    return CODE_RE.search(message.body).group(1)


@override_settings(LOGIN_CODE_RESEND_SECONDS=0)
class LoginCodeModelTests(TestCase):
    def test_issue_returns_six_digit_code_and_stores_only_hash(self):
        login_code, code = LoginCode.issue("Someone@Example.com")
        self.assertRegex(code, r"^\d{6}$")
        self.assertEqual(login_code.email, "someone@example.com")
        self.assertNotIn(code, login_code.code_hash)
        self.assertTrue(login_code.is_usable)

    def test_verify_consumes_code(self):
        _, code = LoginCode.issue("a@example.com")
        self.assertTrue(LoginCode.verify("A@example.com", code))
        with self.assertRaises(LoginCodeError):
            LoginCode.verify("a@example.com", code)

    def test_wrong_code_counts_attempts_then_locks(self):
        _, code = LoginCode.issue("a@example.com")
        for _ in range(5):
            with self.assertRaises(LoginCodeError):
                LoginCode.verify("a@example.com", "000000" if code != "000000" else "111111")
        # Even the right code is refused once the attempt limit is hit.
        with self.assertRaises(LoginCodeError):
            LoginCode.verify("a@example.com", code)

    def test_expired_code_is_rejected(self):
        login_code, code = LoginCode.issue("a@example.com")
        login_code.expires_at = timezone.now() - timedelta(seconds=1)
        login_code.save()
        with self.assertRaises(LoginCodeError):
            LoginCode.verify("a@example.com", code)

    def test_new_code_retires_previous_one(self):
        _, first = LoginCode.issue("a@example.com")
        _, second = LoginCode.issue("a@example.com")
        with self.assertRaises(LoginCodeError):
            LoginCode.verify("a@example.com", first)
        self.assertTrue(LoginCode.verify("a@example.com", second))

    def test_codes_are_per_address(self):
        _, code = LoginCode.issue("a@example.com")
        LoginCode.issue("b@example.com")
        with self.assertRaises(LoginCodeError):
            LoginCode.verify("b@example.com", code)

    @override_settings(LOGIN_CODE_RESEND_SECONDS=30)
    def test_resend_too_soon_is_refused(self):
        LoginCode.issue("a@example.com")
        with self.assertRaisesRegex(LoginCodeError, "just sent"):
            LoginCode.issue("a@example.com")

    @override_settings(LOGIN_CODE_MAX_PER_HOUR=2)
    def test_hourly_limit(self):
        LoginCode.issue("a@example.com")
        LoginCode.issue("a@example.com")
        with self.assertRaisesRegex(LoginCodeError, "Too many codes"):
            LoginCode.issue("a@example.com")


@override_settings(LOGIN_CODE_RESEND_SECONDS=0)
class LoginFlowTests(TestCase):
    def request_code(self, email="new@example.com", **extra):
        return self.client.post(reverse("accounts:login"), {"email": email, **extra})

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Send me a code")

    def test_unknown_address_registers_on_first_verified_code(self):
        response = self.request_code("New@Example.com")
        self.assertRedirects(response, reverse("accounts:verify"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        # No account until the code is verified.
        self.assertFalse(User.objects.filter(email="new@example.com").exists())

        code = code_from_email(mail.outbox[0])
        response = self.client.post(reverse("accounts:verify"), {"code": code})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.user_type, "client")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_existing_user_signs_in_and_honours_next(self):
        user = User.objects.create_user("old@example.com")
        self.request_code("old@example.com", next="/newdomainfiles/")
        code = code_from_email(mail.outbox[0])
        response = self.client.post(reverse("accounts:verify"), {"code": code})
        self.assertRedirects(response, "/newdomainfiles/", fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_unsafe_next_is_ignored(self):
        self.request_code(next="https://evil.example/phish")
        code = code_from_email(mail.outbox[0])
        response = self.client.post(reverse("accounts:verify"), {"code": code})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_wrong_code_shows_error_and_stays_logged_out(self):
        self.request_code()
        code = code_from_email(mail.outbox[0])
        wrong = "000000" if code != "000000" else "111111"
        response = self.client.post(reverse("accounts:verify"), {"code": wrong})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not correct")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_verify_without_requesting_redirects_to_login(self):
        response = self.client.get(reverse("accounts:verify"))
        self.assertRedirects(response, reverse("accounts:login"))

    def test_resend_sends_new_code(self):
        self.request_code()
        response = self.client.post(reverse("accounts:resend"))
        self.assertRedirects(response, reverse("accounts:verify"))
        self.assertEqual(len(mail.outbox), 2)
        # Only the newest code works.
        first, second = (code_from_email(m) for m in mail.outbox)
        self.client.post(reverse("accounts:verify"), {"code": first})
        self.assertNotIn("_auth_user_id", self.client.session)
        self.client.post(reverse("accounts:verify"), {"code": second})
        self.assertIn("_auth_user_id", self.client.session)

    def test_deactivated_user_gets_no_code_but_same_response(self):
        User.objects.create_user("gone@example.com", is_active=False)
        response = self.request_code("gone@example.com")
        self.assertRedirects(response, reverse("accounts:verify"))
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(OPEN_REGISTRATION=False)
    def test_closed_registration_sends_nothing_to_unknown_address(self):
        response = self.request_code("stranger@example.com")
        self.assertRedirects(response, reverse("accounts:verify"))
        self.assertEqual(len(mail.outbox), 0)
        User.objects.create_user("member@example.com")
        self.request_code("member@example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_rate_limit_error_is_shown_on_form(self):
        with override_settings(LOGIN_CODE_RESEND_SECONDS=60):
            self.request_code()
            response = self.request_code()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "just sent")
        self.assertEqual(len(mail.outbox), 1)

    def test_logout(self):
        user = User.objects.create_user("old@example.com")
        self.client.force_login(user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_page_redirects_to_login(self):
        response = self.client.get("/newdomainfiles/")
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next=/newdomainfiles/",
            fetch_redirect_response=False,
        )

    def test_admin_login_uses_code_login(self):
        response = self.client.get("/admin/login/?next=/admin/")
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next=/admin/", fetch_redirect_response=False
        )

    def test_old_register_url_redirects(self):
        response = self.client.get("/register/")
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)


class UserModelTests(TestCase):
    def test_create_superuser_has_no_password_and_admin_type(self):
        user = User.objects.create_superuser("Admin@Example.com")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff and user.is_superuser)
        self.assertEqual(user.user_type, "admin")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(str(user), "admin@example.com")

    def test_email_is_unique(self):
        User.objects.create_user("a@example.com")
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            User.objects.create_user("a@example.com")

    def test_get_by_natural_key_is_case_insensitive(self):
        user = User.objects.create_user("a@example.com")
        self.assertEqual(User.objects.get_by_natural_key("A@EXAMPLE.COM"), user)


class AdminTests(TestCase):
    def test_admin_can_add_user_without_password(self):
        admin = User.objects.create_superuser("admin@example.com")
        self.client.force_login(admin)
        response = self.client.get("/admin/accounts/customuser/add/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "password")
        response = self.client.post(
            "/admin/accounts/customuser/add/",
            {"email": "staff@example.com", "user_type": "client", "first_name": "", "last_name": ""},
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="staff@example.com")
        self.assertFalse(user.has_usable_password())

    def test_admin_change_page_renders(self):
        admin = User.objects.create_superuser("admin@example.com")
        self.client.force_login(admin)
        response = self.client.get(f"/admin/accounts/customuser/{admin.pk}/change/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/accounts/customuser/")
        self.assertEqual(response.status_code, 200)


class MigrationTests(TransactionTestCase):
    """0002 must keep existing accounts and give every one a unique email."""

    def test_fill_missing_emails(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate([("accounts", "0001_initial")])
        OldUser = executor.loader.project_state([("accounts", "0001_initial")]).apps.get_model(
            "accounts", "CustomUser"
        )
        OldUser.objects.create(username="admin", email="", password="x", user_type="admin")
        OldUser.objects.create(username="alice", email="Alice@Example.com", password="x", user_type="client")
        OldUser.objects.create(username="bob", email="alice@example.com", password="x", user_type="client")
        OldUser.objects.create(username="carol", email="carol@example.com", password="x", user_type="client")

        executor = MigrationExecutor(connection)
        executor.migrate([("accounts", "0002_passwordless_email_login")])
        NewUser = executor.loader.project_state(
            [("accounts", "0002_passwordless_email_login")]
        ).apps.get_model("accounts", "CustomUser")

        emails = dict(NewUser.objects.values_list("pk", "email"))
        self.assertEqual(
            sorted(emails.values()),
            ["admin@placeholder.invalid", "alice@example.com", "bob@placeholder.invalid", "carol@example.com"],
        )
        self.assertFalse(hasattr(NewUser, "username"))
