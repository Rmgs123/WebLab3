# Проектный файл urls.py (рядом с settings.py)
from django.contrib import admin
from django.urls import path, include
from home import views as home_views  # Импортируем представление для редиректа
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # URL для django-allauth
    path('accounts/', include('home.accounts_urls')),
    path('home/', include('home.urls')),  # Главная страница, маршрут к home
    path('', home_views.redirect_to_home, name='redirect_to_home'),  # Редирект с корневого URL
]

# Добавьте обработку медиафайлов только в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
