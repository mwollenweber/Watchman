from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Domain(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)


class ZoneList(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    update_interval = models.IntegerField(default=1440)
    last_updated = models.DateTimeField(blank=True, null=True)
