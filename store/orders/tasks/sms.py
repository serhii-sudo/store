# SMS notifications

from celery import shared_task
import requests
from django.conf import settings
from orders.models import Order


@shared_task
def send_order_sms(order_id):
    order = Order.objects.get(id=order_id)

    total_price = sum(item["price"] * item["quantity"] for item in order.history)

    message = f"Devices\n" f"ваш заказ # {order.id}\n" f"успешно оплачен.\n" f"на сумму: {int(total_price)} грн."

    payload = {"recipients": [order.mobile], "sms": {"sender": "MAGAZIN", "text": message}}

    headers = {"Authorization": f"Bearer {settings.TURBOSMS_API_KEY}", "Content-Type": "application/json"}

    response = requests.post("https://api.turbosms.ua/message/send.json", json=payload, headers=headers, timeout=10)

    print("SMS response:", response.json())
