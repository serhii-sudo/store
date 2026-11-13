from django.conf import settings
from google import genai
from pgvector.django import CosineDistance

from products.models import Category
from .models import ProductEmbedding


class ProductSearchService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def search(self, query, limit=5):
        # Определяем производителя, если он указан в запросе.
        query_lower = query.casefold()

        categories = Category.objects.all()

        matched_category = next(
            (category for category in categories if category.name.casefold() in query_lower),
            None,
        )

        # Преобразуем запрос пользователя в вектор.
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
            config={"output_dimensionality": 768},
        )

        query_embedding = response.embeddings[0].values

        # Подготавливаем товары с существующими embeddings
        products = ProductEmbedding.objects.filter(embedding__isnull=False)

        # Если производитель указан, ограничиваем поиск им
        if matched_category:
            products = products.filter(product__categories=matched_category)

        # Ранжируем оставшиеся товары по смысловому сходству
        products = products.annotate(
            distance=CosineDistance(
                "embedding",
                query_embedding,
            )
        ).order_by(
            "distance"
        )[:limit]

        return list(products)
