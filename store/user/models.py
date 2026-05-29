from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)


class TelegramAuth(models.Model):
    code = models.CharField(max_length=6, unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

