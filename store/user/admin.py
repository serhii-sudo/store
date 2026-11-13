from django.contrib import admin

from user.models import CustomUser, TelegramAuth

admin.site.register(CustomUser)


@admin.register(TelegramAuth)
class TelegramAuthAdmin(admin.ModelAdmin):
    list_display = ("code", "telegram_id", "purpose", "is_used", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("telegram_id",)
