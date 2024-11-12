# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Главная страница
    path('add_contact/', views.add_contact, name='add_contact'),  # Маршрут для добавления контактов
    path('home/get_contacts/', views.get_contacts, name='get_contacts'),

    path('send_message/', views.send_message, name='send_message'),  # Маршрут для отправки сообщений
    path('check_new_messages/', views.check_new_messages, name='check_new_messages'),  # Проверка новых сообщений
    path('get_new_messages/<str:chat_user>/', views.get_new_messages, name='get_new_messages'),
    # Получение новых сообщений для чата
    path('load_old_messages/<str:chat_user>/', views.load_old_messages, name='load_old_messages'),
    # загрузка старых сообщений

    path('publish_post/', views.publish_post, name='publish_post'),  # Маршрут для отправки сообщений
    path('check_new_posts/', views.check_new_posts, name='check_new_posts'),  # Проверка новых сообщений
    path('get_new_posts/<str:group_id>/', views.get_new_posts, name='get_new_posts'),
    # Получение новых сообщений для чата
    path('load_old_posts/<str:group_id>/', views.load_old_posts, name='load_old_posts'),
    # загрузка старых сообщений

    path('create/group', views.create_group, name='create_group'),
    path('add_group/', views.add_group, name='add_group'),  # Маршрут для добавления контактов,
]
