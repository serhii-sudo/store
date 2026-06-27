# Тестовая оплата
import base64
import hashlib
import json
import uuid
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from orders.models import Payment, PaymentStatus, Order
from orders.security import verify_liqpay_signature
from store import settings

from orders.tasks.sms import send_order_sms


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order_total = sum(Decimal(item["price"]) * item["quantity"] for item in order.history)

    payment = Payment.objects.create(
        order=order, payment_id=str(uuid.uuid4()), amount=order_total, status=PaymentStatus.PENDING
    )

    data = {
        "public_key": settings.LIQPAY_PUBLIC_KEY,
        "version": "3",  # Версия апи - обязательно! (требование API LiqPay)
        "action": "pay",
        "amount": float(order_total),
        "currency": "UAH",
        "description": f"Order # {order.pk} | {order.initiator.username}",
        "order_id": payment.payment_id,
        # изменяем каждый раз здесь, и в settings!
        "result_url": "https://32fc-37-57-235-224.ngrok-free.app",
        "server_url": "https://32fc-37-57-235-224.ngrok-free.app/orders/payment/callback/",
    }

    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode()).decode()

    signature = base64.b64encode(
        hashlib.sha1((settings.LIQPAY_PRIVATE_KEY + encoded_data + settings.LIQPAY_PRIVATE_KEY).encode()).digest()
    ).decode()

    return redirect(f"https://www.liqpay.ua/api/3/checkout?data={encoded_data}&signature={signature}")


"""
    @csrf_exempt - декоратор, который отключает CSRF-защиту для конкретной view
    используется только для внешних API/webhook (LiqPay, Stripe, PayPal) 
    так как LIQPAY - это не браузер а сервер!!!    
    без @csrf_exempt у тебя будет 403 CSRF error, для LiqPay callback он обязателен!
    Callback (в платежах) — это когда чужой сервис сам звонит твоему серверу и сообщает результат операции
"""


@csrf_exempt
def liqpay_callback(request):
    data = request.POST.get("data")
    signature = request.POST.get("signature")

    if not data or not signature:
        return JsonResponse({"error": "missing data"}, status=400)

    if not verify_liqpay_signature(data, signature):
        return JsonResponse({"error": "invalid signature"}, status=403)

    decoded = json.loads(base64.b64decode(data).decode())

    status = decoded.get("status")
    order_id = decoded.get("order_id")
    transaction_id = decoded.get("transaction_id")

    print("order_id:", order_id)

    payment = Payment.objects.get(payment_id=order_id)

    # idempotency
    if payment.status == PaymentStatus.PAID:
        return JsonResponse({"ok": True})

    payment.transaction_id = transaction_id

    if status != "success":
        payment.status = PaymentStatus.FAILED
        payment.save()
        return JsonResponse({"ok": True})

    # success flow
    payment.status = PaymentStatus.PAID
    payment.paid_at = timezone.now()
    payment.save()

    send_order_sms.delay(payment.order.id)

    return JsonResponse({"ok": True})
