from django.db import models

from products.models import Product
from user.models import CustomUser


class Basket(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)  # удалился пользователь - удалилась его корзины!
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)  # удалился продукт - удалилась корзина!
    quantity = models.SmallIntegerField(default=0)  # изначальное количество товаров в корзине по умолчанию равно 0
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # добавление автоматически даты и времени, когда был добавлен товар

    def __str__(self):
        return (
            f"Корзина для {self.user.username} | "
            f"Продукт: {self.product.name} | "
            f"Цена: {self.product.price} | "
            f"Количество: {self.quantity} | "
            f"Общая стоимость: {self.total_price()}"
        )

    def total_price(self):
        return self.product.price * self.quantity
