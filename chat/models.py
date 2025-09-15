from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Message(models.Model):
    from_who = models.ForeignKey(User, on_delete=models.PROTECT, default=None, related_name="from_user")
    to_who = models.ForeignKey(User, on_delete=models.PROTECT, default=None, related_name="to_user")
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    has_been_seen = models.BooleanField(default=False)

class UserChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=None)
    channel_name = models.TextField()