from datetime import timedelta
from django.forms.models import model_to_dict
from django.contrib.postgres.fields.jsonb import JSONField
from accounts.models import CustomUser
from django.utils import timezone
from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255, unique=True, db_index=True, blank=False, null=False
    )
    is_active = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    max_seats = models.IntegerField(default=0)
    domain = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name


class ClientUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    client = models.OneToOneField(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email}"


class Domain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)
    exp_date = models.DateTimeField(default=None, blank=True, null=True)

    def to_dict(self):
        return model_to_dict(self)

    def __str__(self):
        return self.domain


class NewDomain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    is_processed = models.BooleanField(default=False, blank=True, db_index=True)
    is_expired = models.BooleanField(default=False, db_index=True)
    is_ignored = models.BooleanField(default=False, db_index=True)
    list_display = ["domain", "tld"]

    def to_dict(self):
        return model_to_dict(self)

    def __str__(self):
        return self.domain

class Search(models.Model):
    SEARCH_METHOD_CHOICES = (
        ("regex", "regex"),
        ("substring", "substring"),
        ("strdistance", "strdistance"),
    )

    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    database = models.CharField(
        max_length=255, blank=True, null=True, default="newdomains", db_index=True
    )
    criteria = models.CharField(max_length=255)
    tolerance = models.IntegerField(default=0, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    last_ran = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    update_interval = models.IntegerField(
        default=1440, blank=True, null=True, db_index=True
    )  # in minutes
    is_active = models.BooleanField(default=True, blank=True, db_index=True)
    last_completed = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    is_approved = models.BooleanField(default=True, blank=True, db_index=True)
    method = models.CharField(max_length=20, choices=SEARCH_METHOD_CHOICES)

    list_display = ["client", "method", "criteria"]

    def __str__(self):
        return f"{self.client}: {self.method}('{self.criteria}')"

    class Meta:
        verbose_name = "Search"
        verbose_name_plural = "Searches"


class Match(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=255, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)
    is_reviewed = models.BooleanField(default=False, blank=True, db_index=True)
    is_fp = models.BooleanField(default=False, blank=True, db_index=True)
    is_ignored = models.BooleanField(default=False, blank=True, db_index=True)
    is_public = models.BooleanField(default=False, blank=True, db_index=True)
    has_mx = models.BooleanField(default=False, blank=True, db_index=True)
    has_website = models.BooleanField(default=False, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True)
    has_alerted = models.BooleanField(default=False, db_index=True)
    tlp = models.CharField(max_length=255, db_index=True, default="YELLOW")
    search = models.ForeignKey(Search, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"


class ZoneList(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    update_interval = models.IntegerField(default=28800, blank=True, null=True)
    last_updated = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    last_completed = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    last_diffed = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    last_error = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=32, default="unknown", blank=True, null=True, db_index=True
    )
    enabled = models.BooleanField(default=True, db_index=True)

    url = models.CharField(max_length=255, blank=True, null=True)
    list_display = ["name", "last_updated", "update_interval"]

    def __str__(self):
        return self.name




class WhoisRecord(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class MXRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    record = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, db_index=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)

    def __str__(self):
        return f"{self.record}: {self.ip}"


class AlertConfig(models.Model):
    ALERT_TYPE_CHOICES = (
        ("slack", "slack"),
        ("slackWebhook", "slackWebhook"),
        ("email", "email"),
        ("gmail", "gmail"),
        # ("s3", "s3"),
    )
    alert_type = models.CharField(
        max_length=255, db_index=True, choices=ALERT_TYPE_CHOICES
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_run = models.DateTimeField(auto_now_add=True, blank=True)
    last_completed = models.DateTimeField(auto_now_add=True, blank=True)
    enabled = models.BooleanField(default=True, db_index=True)
    settings = models.JSONField()

    def __str__(self):
        return f"{self.client}: {self.alert_type}"


class WebPage(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    fqdn = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    page = models.CharField(db_index=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    md5 = models.CharField(max_length=32, db_index=True, blank=True, null=True)
    size = models.IntegerField(default=0, db_index=True, blank=True, null=True)
    status_code = models.IntegerField(default=0, db_index=True, blank=True, null=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)


class PingRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    fqdn = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)
    alive = models.BooleanField(default=True, db_index=True)


class ActorRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)
    email = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    first_name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    last_name = models.CharField(max_length=255, db_index=True, blank=True, null=True)


class Watch(models.Model):
    WATCH_TYPE_CHOICES = (
        ("has-mx", "has-mx"),
        ("http200", "http200"),
        ("resolves", "resolves"),
    )
    watch_type = models.CharField(
        max_length=255, db_index=True, choices=WATCH_TYPE_CHOICES
    )
    target = models.CharField(max_length=255, db_index=True)
    expected = models.CharField(max_length=255)
    config = models.JSONField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    last_ran = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    update_interval = models.IntegerField(
        default=1440, blank=True, null=True, db_index=True
    )  # in minutes
    is_active = models.BooleanField(default=True, blank=True, db_index=True)
    last_completed = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    is_approved = models.BooleanField(default=True, blank=True, db_index=True)
    last_error = models.DateTimeField(
        blank=True, null=True, default=timezone.now() - timedelta(days=365)
    )
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=32, default="unknown", blank=True, null=True, db_index=True
    )

    class Meta:
        verbose_name = "Watch"
        verbose_name_plural = "Watches"


class WatchResult(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    hit = models.CharField(max_length=255, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)
    is_reviewed = models.BooleanField(default=False, blank=True, db_index=True)
    is_fp = models.BooleanField(default=False, blank=True, db_index=True)
