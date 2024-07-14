from django.contrib import admin
from Watchman.models import NewDomain, Client, Match, SearchMethod, Search, Domain, WebPage, WhoisRecord, PingRecord


admin.site.register(NewDomain)
admin.site.register(Client)
admin.site.register(Match)
admin.site.register(SearchMethod)
admin.site.register(Search)
admin.site.register(Domain)
admin.site.register(WebPage)
admin.site.register(WhoisRecord)
admin.site.register(PingRecord)
