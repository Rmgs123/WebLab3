# GirlHub/urls.py
from django.contrib import admin
from django.urls import path, include
from home.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home_view, name='home'),  # Главная страница после входа
]