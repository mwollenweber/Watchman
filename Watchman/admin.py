from django.contrib import admin
from Watchman.models import (
    NewDomain,
    Client,
    Match,
    Search,
    Domain,
    WebPage,
    WhoisRecord,
    PingRecord,
    ZoneList,
    ClientUser,
    Watch,
    WatchResult,
    AlertConfig,
    NewCert,
    CTLog,
)


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
admin.site.register(Watch)
admin.site.register(WatchResult)
admin.site.register(AlertConfig)


@admin.register(NewCert)
class NewCertAdmin(admin.ModelAdmin):
    list_display = ["name", "issuer", "not_before", "log", "created"]
    list_filter = ["is_ignored", "is_processed", "is_wildcard"]
    search_fields = ["name"]
    show_full_result_count = False


@admin.register(CTLog)
class CTLogAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "operator",
        "enabled",
        "is_current",
        "status",
        "position",
        "tree_size",
        "entries_skipped",
        "last_updated",
    ]
    list_filter = ["enabled", "is_current", "status", "operator", "is_tiled"]
    search_fields = ["name"]
