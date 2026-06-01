from django.urls import path
from .views import OrderUser, OrderHistory, create_payment, liqpay_callback

urlpatterns = [
    path("create/", OrderUser.as_view(), name="create_order"),
    path("history/", OrderHistory.as_view(), name="history"),
    path("payment/create/<int:order_id>/", create_payment, name="create_payment"),
    path("payment/callback/", liqpay_callback, name="liqpay_callback"),
]
