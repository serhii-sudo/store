import re


def normalize_message(message: str) -> str:
    """Нормализация сообщений от пользователя"""
    message = message.lower().strip()
    message = re.sub(r"[!?,.;:]+$", "", message)
    return message.strip()
