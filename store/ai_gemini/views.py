import json

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .services import GeminiService


@method_decorator(csrf_exempt, name="dispatch")  # отключаем csrf защиту для тестового режима
class GeminiChatView(View):
    def post(self, request):
        data = json.loads(request.body)
        message = data.get("message")

        answer = GeminiService().generate(message)

        return JsonResponse(
            {"answer": answer},
            json_dumps_params={"ensure_ascii": False} # отображение данных в формате кириллицы, Unicode - по умолчанию
        )



