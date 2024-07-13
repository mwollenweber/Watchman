from django.db import models


class Clients(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True, blank=False, null=False)


class Domains(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)


class NewDomains(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_processed = models.BooleanField(default=False, blank=True, db_index=True)
    meh = models.DateTimeField(auto_now_add=True, blank=True)


class Matches(models.Model):
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)


class ZoneList(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    update_interval = models.IntegerField(default=1440, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    next_update = models.DateTimeField(blank=True, null=True)

    # f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
    url = models.CharField(max_length=255, blank=True, null=True)
