# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Главная страница
    path('load_old_messages/<str:chat_user>/', views.load_old_messages, name='load_old_messages'), # загрузка старых сообщений
    path('add_contact/', views.add_contact, name='add_contact'),  # Маршрут для добавления контактов
    path('send_message/', views.send_message, name='send_message'),  # Маршрут для отправки сообщений
    path('check_new_messages/', views.check_new_messages, name='check_new_messages'),  # Проверка новых сообщений
    path('get_new_messages/<str:chat_user>/', views.get_new_messages, name='get_new_messages'),
    path('home/get_contacts/', views.get_contacts, name='get_contacts'),
    # Получение новых сообщений для чата
]