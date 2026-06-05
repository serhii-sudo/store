from decimal import Decimal

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML

from basket.models import Basket
from orders.forms import OrderForm
from orders.models import Order

from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
import json
import base64
import hashlib
import uuid

from .models import Payment, PaymentStatus


class OrderUser(View):
    def post(self, request):
        print(request.POST)
        form = OrderForm(request.POST)
        print(form.errors)
        if form.is_valid():
            order = form.save(commit=False)
            order.initiator = request.user
            order.save()

            """автоматический клининг корзины после сохранения заказа в бд,
            для следующих покупок"""

            basket_items = Basket.objects.filter(user=request.user)

            # сохраняем историю прямо в Order
            order.history = [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price),
                }
                for item in basket_items
            ]
            basket_items.delete()
            order.save()

            return redirect("create_payment", order.id)

        return render(request, "basket/user_basket.html", {"form": form})


# pdf загрузка истории покупок пользователя
class OrderHistoryPdf(View):
    def get(self, request):
        orders = Order.objects.filter(
            initiator=request.user
        ).order_by("-created")

        html_string = render_to_string(
            "orders/orders_pdf.html",
            {
                "orders": orders,
                "user": request.user,
            }
        )

        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            'attachment; filename="orders_history.pdf"'
        )

        return response


# Тестовая оплата
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
        "result_url": "https://a3f1-37-57-235-224.ngrok-free.app ",
        "server_url": "https://a3f1-37-57-235-224.ngrok-free.app/orders/payment/callback/",
    }

    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode()).decode()

    signature = base64.b64encode(
        hashlib.sha1((settings.LIQPAY_PRIVATE_KEY + encoded_data + settings.LIQPAY_PRIVATE_KEY).encode()).digest()
    ).decode()

    return redirect(f"https://www.liqpay.ua/api/3/checkout?data={encoded_data}&signature={signature}")


@csrf_exempt
def liqpay_callback(request):
    print("request.method:", request.method)
    print("request.body:", request.body)

    data = request.POST.get("data")
    print("data:", data)

    if not data:
        return JsonResponse({"error": "no data"}, status=400)

    decoded = json.loads(base64.b64decode(data).decode())

    print("decoded:", decoded)

    status = decoded.get("status")
    order_id = decoded.get("order_id")
    transaction_id = decoded.get("transaction_id")

    print("order_id:", order_id)

    payment = Payment.objects.get(payment_id=order_id)

    if status == "success":
        payment.status = PaymentStatus.PAID
        payment.paid_at = timezone.now()
    else:
        payment.status = PaymentStatus.FAILED

    payment.transaction_id = transaction_id
    payment.save()

    print("status:", payment.status)

    return JsonResponse({"ok": True})
