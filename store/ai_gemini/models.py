import uuid

from django.db import models
from pgvector.django import VectorField

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


# RAG-model будет работать поверх PostgreSQL,
# а pgvector расширит PostgreSQL возможностью хранить векторы и искать по смыслу.
class ProductEmbedding(models.Model):
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

    def __str__(self):
        return f"Embedding: {self.product.name}"
