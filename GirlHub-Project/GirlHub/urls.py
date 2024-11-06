# Проектный файл urls.py (рядом с settings.py)
from django.contrib import admin
from django.urls import path, include
from home import views as home_views  # Импортируем представление для редиректа

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # URL для django-allauth
    path('home/', include('home.urls')),  # Главная страница, маршрут к home
    path('', home_views.redirect_to_home, name='redirect_to_home'),  # Редирект с корневого URL
]
