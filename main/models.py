import datetime

from django.contrib.auth import get_user_model
from django.db import models
from polymorphic.models import PolymorphicModel
from payments.models import Transaction

User = get_user_model()


class Task(PolymorphicModel):
    name = models.CharField(max_length=200, default='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    completed = models.BooleanField(default=False)
    result = models.FileField(upload_to='uploads/', blank=True, null=True)
    payment = models.OneToOneField(Transaction, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f'{self.name}{self.pk}'


class TaskParseSubscribers(Task):
    FOLLOWERS = 'FR'
    FOLLOWING = 'FG'
    TYPE_CHOICES = [
        (FOLLOWERS, 'Followers'),
        (FOLLOWING, 'Following'),
    ]
    instagram_users = models.TextField()
    quantity_users = models.PositiveIntegerField(default=1)
    task_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=FOLLOWERS)

    def total_sum(self):
        return len(self.instagram_users.split(',')) * self.quantity_users


class TaskParseLikes(Task):
    posts = models.TextField()
    quantity_users = models.PositiveIntegerField(default=1)

    def total_sum(self):
        return len(self.posts.split('\n')) * self.quantity_users


class IGAccount(models.Model):
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    last_use = models.DateTimeField(auto_now=True)
    in_use = models.BooleanField(default=False)
