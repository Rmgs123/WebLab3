from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contacts = models.ManyToManyField('self', symmetrical=False, related_name='contact_users')
    groups = models.ManyToManyField('Group', symmetrical=False, related_name='groups_user')
    image = models.ImageField(upload_to='profile_images/', default='../static/home/default.png')

    def __str__(self):
        return self.user.username


class Group(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField('Profile', through=r'GroupMemberStatus', symmetrical=False,
                                     related_name='members_group')
    image = models.ImageField(upload_to='group_images/', default='../static/home/default.png')

    def __str__(self):
        return str(self.id)


class GroupMemberStatus(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'member')

    def __str__(self):
        return f"{self.member} in {self.group} - Read: {self.is_read}"


class Post(models.Model):
    group_sender = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_post')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='group_chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_sender

    class Meta:
        ordering = ['timestamp']


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'From {self.sender} to {self.receiver}'

    class Meta:
        ordering = ['timestamp']
