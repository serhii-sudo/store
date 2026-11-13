import json
import uuid

from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from google.genai.errors import ClientError

from .constans import SOCIAL_MESSAGES
from .models import GeminiMessage
from .services import GeminiService
from .product_search import ProductSearchService
from .utils.text_normalizer import normalize_message


@method_decorator(csrf_exempt, name="dispatch")
class GeminiChatView(View):
    """
    Обработка Gemini-чата.

    Возможности:
    - Доступ только для авторизованных пользователей.
    - Сохранение истории сообщений.
    - Семантический поиск товаров через ProductSearchService.
    - Формирование ссылок на страницы найденных товаров.
    - Генерация ответа с помощью Gemini.
    """

    def get(self, request, conversation_id=None):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401,
            )

        if not conversation_id:
            return JsonResponse({"messages": []})

        messages = GeminiMessage.objects.filter(
            user=request.user,
            conversation_id=conversation_id,
        ).order_by("created_at")

        return JsonResponse(
            {
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ]
            },
            json_dumps_params={"ensure_ascii": False},
        )

    def post(self, request, conversation_id=None):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401,
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400,
            )

        message = data.get("message")

        if not isinstance(message, str) or not message.strip():
            return JsonResponse(
                {"error": "Message is required"},
                status=400,
            )

        message = message.strip()

        # Создаём новую беседу, если её ещё нет.
        if not conversation_id:
            conversation_id = uuid.uuid4()

        # Сохраняем сообщение пользователя.
        GeminiMessage.objects.create(
            user=request.user,
            conversation_id=conversation_id,
            role="user",
            content=message,
        )

        try:
            products_context = []
            # Нормализуем сообщение для сравнения.
            normalized_message = normalize_message(message)

            if normalized_message in SOCIAL_MESSAGES:
                # На приветствие отвечаем без поиска товаров.
                prompt = f"""
        Ты — AI-помощник интернет-магазина.

        Пользователь написал: {message}

        Поздоровайся в ответ на русском языке.
        Кратко предложи помочь с выбором товара.
        Не перечисляй товары и не создавай ссылки.
        """

                answer = GeminiService().generate(prompt)
                products = []

            else:
                # 2. Ищем товары через семантический поиск.
                products = ProductSearchService().search(
                    message,
                    limit=5,
                )

                # 3. Формируем контекст с названиями и URL товаров.
                if products:
                    product_lines = []

                    for item in products:
                        product = item.product

                        product_url = reverse(
                            "product_detail",
                            kwargs={"id": product.id},
                        )

                        product_lines.append(f"Название: {product.name}\nСсылка: {product_url}")

                    products_context = "\n\n".join(product_lines)

                else:
                    products_context = "Подходящие товары не найдены."

            # 3. Формируем запрос к Gemini.
            prompt = f"""
Ты — AI-помощник интернет-магазина.

Отвечай на русском языке.
Помогай пользователям находить товары в каталоге магазина.

Правила:
- Рекомендуй только товары из предоставленного списка.
- Не придумывай названия, цены и характеристики товаров.
- Не утверждай, что товар есть в наличии, если это не указано.
- Не создавай ссылки и не используй Markdown-разметку.
- Называй рекомендованные товары точно так, как они указаны в результатах поиска.
- Если подходящих товаров нет, сообщи об этом.
- Отвечай понятно и по существу.


- Если пользователь здоровается, поздоровайся в ответ.
- Если пользователь благодарит, вежливо поблагодари в ответ.
- Если пользователь задаёт обычный вопрос, ответь на него по существу.
- Не предлагай товары без соответствующего запроса пользователя.
- Если пользователь ищет товар, рекомендуй только товары из предоставленного списка.
- Не придумывай названия, цены и характеристики товаров.
- Не создавай ссылки и не используй Markdown-разметку.

Сообщение пользователя:
{message}

Результаты поиска по каталогу магазина:
{products_context}
"""

            # 4. Получаем ответ Gemini.
            answer = GeminiService().generate(prompt)

        except ClientError as error:
            if error.code == 429:
                return JsonResponse(
                    {"error": ("Gemini API временно недоступен. " "Превышена квота.")},
                    status=429,
                )

            raise

        # 5. Сохраняем ответ Gemini.
        GeminiMessage.objects.create(
            user=request.user,
            conversation_id=conversation_id,
            role="gemini",
            content=answer,
        )

        # 6. Возвращаем ответ фронтенду.
        return JsonResponse(
            {
                "answer": answer,
                "conversation_id": str(conversation_id),
                "products": [
                    {
                        "name": item.product.name,
                        "url": reverse(
                            "product_detail",
                            kwargs={"id": item.product.id},
                        ),
                    }
                    for item in products
                ],
            },
            json_dumps_params={"ensure_ascii": False},
        )

    def delete(self, request, conversation_id=None):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401,
            )

        if not conversation_id:
            return JsonResponse(
                {"error": "Conversation ID is required"},
                status=400,
            )

        GeminiMessage.objects.filter(
            user=request.user,
            conversation_id=conversation_id,
        ).delete()

        return JsonResponse(
            {
                "message": "Chat history successfully deleted!",
            },
            json_dumps_params={"ensure_ascii": False},
        )
