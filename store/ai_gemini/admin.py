from django.contrib import admin

from ai_gemini.models import GeminiMessage


@admin.register(GeminiMessage)
class GeminiMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "conversation_id",
        "role",
        "short_content",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    @admin.display(description="content")
    def short_content(self, obj):
        return obj.content[:300]
