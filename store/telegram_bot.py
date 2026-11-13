# ruff: noqa: E402
import os
from datetime import timedelta

from telegram.constants import ParseMode

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store.settings")

import django

django.setup()

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from telegram.ext import ApplicationBuilder, CommandHandler

from user.models import CustomUser, TelegramAuthPurpose, TelegramAuth

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


@transaction.atomic
def process_telegram_code(code, telegram_id):
    obj = TelegramAuth.objects.select_for_update(of=("self",)).filter(code=code).first()

    if not obj:
        return "not_found"

    if obj.is_used:
        return "already_used"

    if timezone.now() - obj.created_at > timedelta(minutes=1):
        return "expired"

    # Сценарий 1: привязка Telegram к существующему аккаунту
    if obj.purpose == TelegramAuthPurpose.LINK:
        if not obj.user_id:
            return "user_not_found"

        user = obj.user

        # Проверяем, не привязан ли к аккаунту другой Telegram
        if user.telegram_id and user.telegram_id != telegram_id:
            return "account_already_linked"

        # Проверяем, не принадлежит ли Telegram ID другому аккаунту
        if CustomUser.objects.filter(telegram_id=telegram_id).exclude(pk=user.pk).exists():
            return "telegram_already_linked"

        user.telegram_id = telegram_id
        user.save(update_fields=["telegram_id"])

    # Вход через Telegram
    elif obj.purpose == TelegramAuthPurpose.LOGIN:
        user = CustomUser.objects.filter(telegram_id=telegram_id).first()

        if not user:
            return "telegram_not_linked"

    else:
        return "unknown_purpose"

    # Отмечаем код использованным
    obj.telegram_id = telegram_id
    obj.is_used = True
    obj.save(update_fields=["telegram_id", "is_used"])

    return "success"


async def start(update, context):
    text = update.message.text
    telegram_id = update.message.from_user.id

    parts = text.split()

    if len(parts) < 2:
        await update.message.reply_text("Нет кода")
        return

    code = parts[1].strip()

    result = await sync_to_async(process_telegram_code)(
        code,
        telegram_id,
    )

    if result == "not_found":
        await update.message.reply_text("🔴 Код не найден")

    elif result == "already_used":
        await update.message.reply_text("🔴 Этот код уже использован!!!")

    elif result == "expired":
        await update.message.reply_text(
            "🟡 Код устарел. Вернитесь на сайт и получите новый.\n\n" "⮕  http://127.0.0.1:8000/"
        )

    elif result == "user_not_found":
        await update.message.reply_text("🟡 Пользователь для привязки не найден")

    elif result == "account_already_linked":
        await update.message.reply_text("🟡 К аккаунту уже привязан другой Telegram!")

    elif result == "telegram_not_linked":
        await update.message.reply_text(
            "🟡 Этот Telegram ещё не привязан к аккаунту.\n\n"
            "Перейдите на сайт, зарегистрируйтесь или войдите в существующий аккаунт, "
            "а затем привяжите Telegram в личном кабинете.\n\n"
            "После этого вы сможете использовать Telegram, для входа на сайт.\n\n"
            "⮕  http://127.0.0.1:8000/"
        )

    elif result == "telegram_already_linked":
        await update.message.reply_text("🟡 Этот Telegram уже привязан к другому аккаунту!")

    elif result == "unknown_purpose":
        await update.message.reply_text("🔴 Неизвестный тип операции!")

    elif result == "success":
        await update.message.reply_text(
            "<b>🟢 Операция успешно подтверждена!</b>\n\n"
            "Теперь вернитесь на сайт:\n"
            "⮕ <a href='http://127.0.0.1:8000/'>Перейти на сайт</a>",
            parse_mode=ParseMode.HTML,
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
