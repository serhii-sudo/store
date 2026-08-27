from django.urls import path

from ai_gemini.views import GeminiChatView

urlpatterns = [
    path("chat/", GeminiChatView.as_view(), name="gemini-chat"),
    path("chat/<uuid:conversation_id>/",  GeminiChatView.as_view(), name="gemini-chat-history")
]
