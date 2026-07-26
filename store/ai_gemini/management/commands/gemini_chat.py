from django.core.management.base import BaseCommand

from ai_gemini.services import GeminiService

"""
По такому сценарию, а именно:
    - management/commands/gemini.chat без суффикса .py!
    - каждое приложение может иметь свои собственные management-команды, и Django автоматически их найдет!
    - и позволит запустить напрямую в shell  через ./manage.py gemini_chat
"""


class Command(BaseCommand):
    help = "Interactive Gemini chat"

    def handle(self, *args, **options):
        ai = GeminiService()

        while True:
            prompt = input("Вы: ")

            if prompt.lower() == "exit":
                break

            print(f"\nGemini: {ai.generate(prompt)}\n")
