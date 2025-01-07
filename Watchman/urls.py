from django.contrib import admin
from django.urls import path
from Watchman import views

urlpatterns = [
    path("", views.index),
    path("accounts/login/", views.login),
    path("register/", views.signup),
    path("logout", views.logout_view),
    path("api/zonestatus/", views.zone_status),
    path("api/hits/", views.hits),
    path("api/public_hits/", views.public_hits),
    path("api/search/", views.search),
    path("api/isnod/", views.is_nod),
    path("api/newdomains/", views.new_domains),
    path("admin/", admin.site.urls),
]
