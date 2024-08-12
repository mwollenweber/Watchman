from django.contrib import admin
from django.urls import path
from Watchman import views

urlpatterns = [
    path("", views.index),
    path("accounts/login/", views.login),
    path("register/", views.signup),
    path("logout", views.logout_view),
    path("zonestatus/", views.zone_status),
    path("hits/", views.hits),
    path("newdomains/", views.new_domains),
    path("admin/", admin.site.urls),
]
