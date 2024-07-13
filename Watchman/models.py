from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True, blank=False, null=False)
    is_active = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    max_seats = models.IntegerField(default=0)


class Domain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)


class NewDomain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    tld = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    first_seen = models.DateTimeField(auto_now_add=True, blank=True)
    is_processed = models.BooleanField(default=False, blank=True, db_index=True)
    meh = models.DateTimeField(auto_now_add=True, blank=True)


class Match(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True, blank=True, db_index=True)


class ZoneList(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    update_interval = models.IntegerField(default=1440, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    next_update = models.DateTimeField(blank=True, null=True)

    # f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
    url = models.CharField(max_length=255, blank=True, null=True)



class SearchMethod(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    is_enabled = models.BooleanField(default=True, blank=True, db_index=True)


class Search(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    method = models.ForeignKey(SearchMethod, on_delete=models.CASCADE)
    criteria = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_ran = models.DateTimeField(blank=True, null=True)
    interval = models.IntegerField(default=1440, blank=True, null=True) #in minutes






