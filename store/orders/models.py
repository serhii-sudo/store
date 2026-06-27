from django.db import models
from user.models import CustomUser


class Order(models.Model):
    email = models.EmailField(max_length=150)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    mobile = models.CharField(blank=False, null=False, max_length=20)
    checkbox = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    history = models.JSONField(default=dict)
    initiator = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Order # {self.pk}: {self.username}, {self.email}, {self.mobile}"

    class Meta:
        ordering = ["-created"]


# Статус оплаты
class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"


"""
Через какого провайдера оплатили? У нас 1 провайдер, но мы оставим возможность масштабирование в будущем,
для других провайдеров
"""


class PaymentProvider(models.TextChoices):
    LIQPAY = "liqpay", "LiqPay"


# LiqPay
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PaymentProvider, default=PaymentProvider.LIQPAY)
    payment_id = models.CharField(max_length=64, unique=True)
    transaction_id = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatus, default=PaymentStatus.PENDING)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.id} | {self.amount} UAH | {self.status}"
