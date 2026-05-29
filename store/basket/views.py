from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import View

from basket.models import Basket
from orders.forms import OrderForm
from products.models import Product


class AddInBasket(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        basket_item, created = Basket.objects.get_or_create(user=request.user, product=product)

        # лаконичное решение:
        basket_item.quantity = basket_item.quantity + 1 if not created else 1
        basket_item.save()

        messages.success(request, "✅ Товар добавлен в корзину!")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class BasketView(View):
    template_patch = "basket/user_basket.html"

    def get(self, request):
        basket_items = Basket.objects.filter(user=request.user)  # посмотреть содержимое корзины, продукция юзера
        total_sum = sum(item.total_price() for item in basket_items)
        result_of_all_price = [item.total_price() for item in basket_items]

        items_with_total = []
        for item in basket_items:
            items_with_total.append({"item": item, "total_price": item.total_price()})  # сам объект корзины

        for item in basket_items:
            print(item.product.price)
        """Подставляем автоматом из request.user.username через backend в поле формы username,
        чтобы поле уже было заполнено, и 
         'readonly': 'readonly' -  поставлено только на чтение(изменение поля с фронта - запрещено)
       """
        form = OrderForm(initial={"username": request.user.username})

        return render(
            request,
            self.template_patch,
            {
                "basket_product": basket_items,
                "total_sum": total_sum,
                "result_of_all_price": result_of_all_price,
                "items_with_total": items_with_total,
                "form": form,
            },
        )


class DelBasket(View):
    def post(self, request, id):  # удаление товара из корзины
        basket = Basket.objects.get(id=id)
        basket.delete()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
