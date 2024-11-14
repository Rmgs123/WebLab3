from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('delete/', views.home_delete, name='home_delete'),
    path('clear/', views.home_clear, name='home_clear'),
    path('pop_back/', views.home_pop_back, name='home_pop_back'),

    path('add_contact/', views.add_contact, name='add_contact'),
    path('get_contacts/', views.get_contacts, name='get_contacts'),
    path('get_groups/', views.get_groups, name='get_groups'),

    path('send_message/', views.send_message, name='send_message'),
    path('check_new_messages/', views.check_new_messages, name='check_new_messages'),

    path('get_new_messages/<str:chat_user>/', views.get_new_messages, name='get_new_messages'),
    path('load_old_messages/<str:chat_user>/', views.load_old_messages, name='load_old_messages'),

    path('publish_post/', views.publish_post, name='publish_post'),
    path('check_new_posts/', views.check_new_posts, name='check_new_posts'),

    path('get_new_posts/<str:group_id>/', views.get_new_posts, name='get_new_posts'),
    path('load_old_posts/<str:group_id>/', views.load_old_posts, name='load_old_posts'),

    path('create/group', views.create_group, name='create_group'),
    path('add_group/', views.add_group, name='add_group'),
]
