from django.conf import settings
from google import genai


# Настройка сервиса Gemini
class GeminiService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,  # prompt — текст, который ты отправляешь модели
        )
        return response.text
