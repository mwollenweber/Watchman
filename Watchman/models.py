from datetime import timedelta
from django.utils import timezone
from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True, blank=False, null=False)
    is_active = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    max_seats = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Domain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)

    def __str__(self):
        return self.domain


class NewDomain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_processed = models.BooleanField(default=False, blank=True, db_index=True)
    meh = models.DateTimeField(auto_now_add=True, blank=True)
    list_display = ['domain', 'tld']

    def __str__(self):
        return self.domain


class Match(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)

    list_display = ['domain', 'client', 'is_new']

    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'


class MatchHit(models.Model):
    hit = models.CharField(max_length=255, db_index=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)


class ZoneList(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    update_interval = models.IntegerField(default=28800, blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    last_completed = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    last_diffed = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    last_error = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=32, default="unknown", blank=True, null=True, db_index=True)
    enabled = models.BooleanField(default=True, db_index=True)

    url = models.CharField(max_length=255, blank=True, null=True)
    list_display = ['name', 'last_updated', 'update_interval']

    def __str__(self):
        return self.name


class SearchMethod(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    is_enabled = models.BooleanField(default=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.name}"


class Search(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    method = models.ForeignKey(SearchMethod, on_delete=models.CASCADE)
    database = models.CharField(max_length=255, blank=True, null=True, default="newdomains", db_index=True)
    criteria = models.CharField(max_length=255)
    tolerance = models.IntegerField(default=0, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    last_ran = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))
    update_interval = models.IntegerField(default=1440, blank=True, null=True, db_index=True)  # in minutes
    is_active = models.BooleanField(default=True, blank=True, db_index=True)
    last_completed = models.DateTimeField(blank=True, null=True, default=timezone.now() - timedelta(days=365))

    list_display = ['client', 'method', 'criteria']

    def __str__(self):
        return f"{self.client}: {self.method}('{self.criteria}')"

    class Meta:
        verbose_name = 'Search'
        verbose_name_plural = 'Searches'




class WhoisRecord(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class MXRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    record = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, db_index=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)


class WebPage(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
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
    alive = models.BooleanField(default=False, db_index=True)


class ActorRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(db_index=True, blank=True, null=True)
    email = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    first_name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    last_name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    alias = models.CharField(max_length=255, db_index=True, blank=True, null=True)
