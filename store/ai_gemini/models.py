import uuid

from django.db import models
from pgvector.django import VectorField

from store import settings


class GeminiMessage(models.Model):
    """Модель для сохранения истории чата."""

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
        verbose_name = "Gemini Message"
        verbose_name_plural = "Gemini Messages"

    def __str__(self):
        return f"{self.user.username} | {self.role} | {self.content[:50]}"


class ProductEmbedding(models.Model):
    """
    RAG-model будет работать поверх PostgreSQL,
    а pgvector расширит PostgreSQL возможностью хранить векторы и искать по смыслу.
    """

    product = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="embedding_data",
    )

    content = models.TextField()

    embedding = VectorField(
        dimensions=768,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "embedding_data"
        verbose_name_plural = "embedding_data"

    def __str__(self):
        return f"Embedding: {self.product.name}"
