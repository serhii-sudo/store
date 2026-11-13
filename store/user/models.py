from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя, расширяющая стандартный AbstractUser."""

    email = models.EmailField(unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)


class TelegramAuthPurpose(models.TextChoices):
    """
    Определяет назначение кода Telegram-аутентификации.

    TextChoices задаёт пары значений в формате value/label:
    value — значение, сохраняемое в БД;
    label — человекочитаемое название для отображения.
    """

    LOGIN = "login", "Вход"
    LINK = "link", "Привязка"


class TelegramAuth(models.Model):
    """Модель Телеграм аутентификации."""

    code = models.CharField(max_length=6, unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(
        max_length=6,
        choices=TelegramAuthPurpose.choices,
        default=TelegramAuthPurpose.LOGIN,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telegram Auth"
        verbose_name_plural = "Telegram Auth"
