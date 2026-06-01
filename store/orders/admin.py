from django.contrib import admin

from orders.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "payment_id",
        "transaction_id",
        "status",
        "amount",
        "created_at",
        "paid_at",
        "get_username",
        "get_address",
        "get_mobile",
    )

    """
    добавляем и регистрируем дополнительные поля из других бд, чтобы
    удобно было видно конечного юзера, который сделал покупку
    """

    def get_username(self, obj):
        return obj.order.initiator.username

    def get_address(self, obj):
        return obj.order.address

    def get_mobile(self, obj):
        return obj.order.mobile


admin.site.register(Payment, PaymentAdmin)
