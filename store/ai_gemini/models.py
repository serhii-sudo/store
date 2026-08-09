import uuid

from django.db import models

from store import settings


# Модель в которую будем сохранять историю чата
class GeminiMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gemini_messages",
    )
    conversation_id = models.UUIDField(default=uuid.uuid4)
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("gemini", "Gemini"),
        ],
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "conversation_id"],
            ),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.role} | {self.content[:50]}"