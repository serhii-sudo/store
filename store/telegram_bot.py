import os
from datetime import timedelta

import django

from asgiref.sync import sync_to_async
from django.utils import timezone
from telegram.ext import ApplicationBuilder, CommandHandler

# ------------------------
# Django setup (ОБЯЗАТЕЛЬНО ВВЕРХУ)
# ------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store.settings")
django.setup()

from user.models import TelegramAuth, CustomUser

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# ------------------------
# /start handler
# ------------------------
async def start(update, context):
    text = update.message.text
    telegram_id = update.message.from_user.id

    print("RAW TEXT:", text)

    parts = text.split()
    print("parts:", parts)

    if len(parts) < 2:
        await update.message.reply_text("Нет кода")
        return

    code = parts[1].strip()
    print("code:", code)

    # 1. ищем код
    obj = await sync_to_async(TelegramAuth.objects.filter(code=code).first)()

    if not obj:
        await update.message.reply_text("Код не найден")
        return

    if timezone.now() - obj.created_at > timedelta(minutes=1):
        await update.message.reply_text(
            "Код устарел!!! Вернись на сайт, обновите страницу для генерации нового кода" " и попробуй снова."
        )
        return

    # 2. помечаем использованным
    obj.telegram_id = telegram_id
    obj.is_used = True
    await sync_to_async(obj.save)()

    # 3. создаём пользователя
    user, created = await sync_to_async(CustomUser.objects.get_or_create)(
        telegram_id=telegram_id, defaults={"username": f"tg_{telegram_id}"}
    )

    # 4. сохраняем
    user.telegram_id = telegram_id
    await sync_to_async(user.save)()

    await update.message.reply_text("Вход подтвержден! Вернитесь на сайт")


# ------------------------
# async def handle_message(update, context):
#     await update.message.reply_text("Отправь /start + код")


# ------------------------
# bot init
# ------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
# app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
