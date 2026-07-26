from django.urls import path

from ai_gemini.views import GeminiChatView

urlpatterns = [
    path("chat/", GeminiChatView.as_view(), name="chat"),

]
