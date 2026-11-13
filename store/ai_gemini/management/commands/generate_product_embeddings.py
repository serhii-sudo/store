import json

from django.conf import settings
from django.core.management.base import BaseCommand
from google import genai

from products.models import Product
from ai_gemini.models import ProductEmbedding


class Command(BaseCommand):
    help = "Generate embeddings for all products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Process only the specified number of products",
        )

    def handle(self, *args, **options):
        limit = options["limit"]

        if limit is not None and limit < 1:
            self.stderr.write(self.style.ERROR("--limit должен быть больше нуля."))
            return

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        products = Product.objects.select_related("categories").order_by("id")

        if limit is not None:
            products = products[:limit]

        total = len(products)

        if total == 0:
            self.stdout.write("Товары не найдены.")
            return

        self.stdout.write(f"Товаров для обработки: {total}")

        created = 0
        updated = 0
        failed = 0

        for index, product in enumerate(products, start=1):
            specifications = json.dumps(
                product.specifications,
                ensure_ascii=False,
            )

            content = (
                f"Название: {product.name}. "
                f"Категория: {product.categories.name}. "
                f"Характеристики: {specifications}"
            )

            try:
                result = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=content,
                    config={"output_dimensionality": 768},
                )

                embedding = result.embeddings[0].values

                if len(embedding) != 768:
                    raise ValueError(f"Ожидалось 768 чисел, получено {len(embedding)}.")

                _, was_created = ProductEmbedding.objects.update_or_create(
                    product=product,
                    defaults={
                        "content": content,
                        "embedding": embedding,
                    },
                )

                if was_created:
                    created += 1
                    status = "Создан"
                else:
                    updated += 1
                    status = "Обновлён"

                self.stdout.write(self.style.SUCCESS(f"[{index}/{total}] {status}: {product.name}"))

            except Exception as error:
                failed += 1
                self.stderr.write(self.style.ERROR(f"[{index}/{total}] Ошибка для " f"{product.name}: {error}"))

        self.stdout.write("\nРезультаты генерации:")
        self.stdout.write(f"Создано: {created}")
        self.stdout.write(f"Обновлено: {updated}")
        self.stdout.write(f"Ошибок: {failed}")

        if failed:
            self.stdout.write(self.style.WARNING("Некоторые товары не обработаны. " "Проверь ошибки и повтори запуск."))
        else:
            self.stdout.write(self.style.SUCCESS("Генерация завершена успешно."))
