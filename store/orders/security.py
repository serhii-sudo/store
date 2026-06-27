import hashlib
import base64
import hmac
from django.conf import settings


def verify_liqpay_signature(data: str, signature: str) -> bool:
    """
    LiqPay, специально “вшивают” секретный ключ в начало и конец чтобы:
        - нельзя было подделать data
        - нельзя было просто взять signature
        - + нужен секрет private_key
        - нельзя было изменить письмо
        - нельзя было создать подпись без пароля

    """
    # подготовка данных для хеширования
    sign_str = f"{settings.LIQPAY_PRIVATE_KEY}{data}{settings.LIQPAY_PRIVATE_KEY}"

    sha1_hash = hashlib.sha1(sign_str.encode("utf-8")).digest()
    expected = base64.b64encode(sha1_hash).decode("utf-8")

    return hmac.compare_digest(expected, signature)


""" 
    hmac.compare_digest = защищённое сравнение строк без утечки времени
    время всегда одинаковое, независимо от совпадения
    hmac.compare_digest() — это функция для безопасного сравнения строк (или байт), чаще всего — подписей, токенов, хэше
    проверить, что подпись точно совпадает, но не дать атакующему возможность подобрать её по времени ответа
    hmac.compare_digest — это безопасное сравнение строк, которое проверяет равенство, 
    но не даёт утечь информации через время ответа.
"""
