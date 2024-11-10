# home/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('change/email/', views.change_email_view, name='account_change_email'),
    path('settings', views.settings, name='account_settings'),
    path('change/image', views.change_image, name='account_change_image'),
    path('change/username', views.change_username, name='account_change_username'),
]
