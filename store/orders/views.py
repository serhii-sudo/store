from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from django.views import View

from weasyprint import HTML

from basket.models import Basket
from orders.forms import OrderForm
from orders.models import Order

from django.shortcuts import redirect


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
