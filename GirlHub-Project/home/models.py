# home/models.py
from django.contrib.auth.models import User
from django.db import models


# Модель для профиля пользователя, если нужна дополнительная информация
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contacts = models.ManyToManyField('self', symmetrical=False, related_name='contact_users')
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')

    def __str__(self):
        return self.user.username


# Модель для сообщений между пользователями
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)  # Поле для текста сообщения
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)  # Новое поле для изображения
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'From {self.sender} to {self.receiver}'

    class Meta:
        ordering = ['timestamp']
