# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Главная страница
    path('add_contact/', views.add_contact, name='add_contact'),  # Маршрут для добавления контактов
    path('send_message/', views.send_message, name='send_message'),  # Маршрут для отправки сообщений
]
