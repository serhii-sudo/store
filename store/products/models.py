from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=69)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=69)
    image = models.ImageField(upload_to="image")
    price = models.DecimalField(decimal_places=2, max_digits=9)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    categories = models.ForeignKey(to=Category, on_delete=models.PROTECT)  # on_delete=models.PROTECT - в продакшн!
    specifications = models.JSONField(default=list,  blank=True)


    class Meta:
        ordering = ["-created_at"]  # Упорядочивание по дате создания (самые новые первые)

    def __str__(self):
        return f"имя продукта: {self.name} | стоимость единицы: {self.price}"
