from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from Watchman import views

urlpatterns = [
    path("", views.index, name="index"),
    # Sign-in is by emailed one-time code; see the accounts app.
    path("accounts/", include("accounts.urls")),
    path("register/", RedirectView.as_view(pattern_name="accounts:login", query_string=True)),
    path("logout", RedirectView.as_view(pattern_name="accounts:logout", query_string=True)),
    path("admin/login/", RedirectView.as_view(pattern_name="accounts:login", query_string=True)),
    path("api/zonestatus/", views.zone_status),
    path("api/hits/", views.hits),
    path("api/public_hits/", views.public_hits),
    path("api/search/", views.search),
    path("api/isnod/", views.is_nod),
    path("api/newdomains/", views.new_domains),
    path("newdomainfiles/", views.newdomain_files),
    path("newdomainfiles/<str:key>", views.newdomain_file, name="newdomain_file"),
    path("admin/", admin.site.urls),
]
