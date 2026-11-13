from django.db import models


class Category(models.Model):
    """Модель выбора категорий"""

    name = models.CharField(max_length=69)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    """Модель описания продуктов."""

    name = models.CharField(max_length=69)
    image = models.ImageField(upload_to="image")
    price = models.DecimalField(decimal_places=2, max_digits=9)
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    categories = models.ForeignKey(to=Category, on_delete=models.PROTECT)  # on_delete=models.PROTECT - в продакшн!
    specifications = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"имя продукта: {self.name} | стоимость единицы: {self.price}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved
