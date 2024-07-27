from django.contrib import admin
from django.urls import path
from Watchman import views

urlpatterns = [
    path('', views.index),
    path('accounts/login/', views.user_login),
    #path('logout', logout),
    path('zonestatus/', views.zone_status),
    #path('hits', views.hits),
    path("admin/", admin.site.urls),
]
