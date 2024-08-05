from django.contrib import admin
from Watchman.models import NewDomain, Client, Match, Search, Domain, WebPage, WhoisRecord, PingRecord, ZoneList, ClientUser


admin.site.register(NewDomain)
admin.site.register(ClientUser)
admin.site.register(Client)
admin.site.register(Match)
admin.site.register(Search)
admin.site.register(Domain)
admin.site.register(WebPage)
admin.site.register(WhoisRecord)
admin.site.register(PingRecord)
admin.site.register(ZoneList)
