import json
import uuid

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from google.genai.errors import ClientError

from .models import GeminiMessage
from .services import GeminiService


@method_decorator(csrf_exempt, name="dispatch")
class GeminiChatView(View):
    """
    Проверки на аутентификацию пользователей в методах get/post:
    - БД — чтобы сообщение принадлежало конкретному CustomUser.
    - Историю чатов — чтобы анонимный пользователь не создавал, не использовал чужие разговоры.
    - Gemini API — чтобы любой посетитель не мог расходовать твою квоту.
    - Бизнес-логику — Gemini-чат у тебя является функцией авторизованного пользователя
    """

    def get(self, request, conversation_id=None):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        print("USER:", request.user)
        print("CONVERSATION_ID:", conversation_id)

        if not conversation_id:
            return JsonResponse({"messages": []})

        messages = GeminiMessage.objects.filter(
            user=request.user,
            conversation_id=conversation_id,
        ).order_by("created_at")
        print("MESSAGES COUNT:", messages.count())

        return JsonResponse(
            {
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ]
            }
        )

    def post(self, request, conversation_id=None):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        data = json.loads(request.body)

        message = data.get("message")

        if not message:
            return JsonResponse(
                {"error": "Message is required"},
                status=400,
            )

        # Если conversation_id ещё нет —
        # создаём новую беседу

        if not conversation_id:
            conversation_id = uuid.uuid4()

        # Сохраняем сообщение пользователя

        GeminiMessage.objects.create(
            user=request.user,
            conversation_id=conversation_id,
            role="user",
            content=message,
        )

        # Получаем ответ Gemini
        try:
            answer = GeminiService().generate(message)

        except ClientError as e:
            if e.code == 429:
                return JsonResponse(
                    {"error": "Gemini API временно недоступен. Превышена квота."},
                    status=429,
                )
            raise
        # raise - Все неизвестные ошибки нормально уходят дальше
        # По сути, мы обрабатываем только статус 429, если будет другой статус -> то он,
        # будет уходить следующему уровню обработки, но нет гарантии, что буде другой статус корректно,
        # скорее всего сервер выдаст статус 500.

        # Сохраняем ответ Gemini

        GeminiMessage.objects.create(
            user=request.user,
            conversation_id=conversation_id,
            role="gemini",
            content=answer,
        )

        return JsonResponse(
            {
                "answer": answer,
                "conversation_id": str(conversation_id),
            },
            json_dumps_params={"ensure_ascii": False},
        )

    # json_dumps_params={"ensure_ascii": False} -> относится к тому, как Python сериализует данные в JSON
    # Unicode-символы могут быть представлены escape-последовательностями.
    # Например, русский текст может выглядеть примерно так: \u041f\u0440\u0438\u0432\u0435\u0442
