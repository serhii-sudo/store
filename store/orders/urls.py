from django.urls import path

from .providers.liqpay import create_payment, liqpay_callback
from .views import OrderUser,OrderHistoryPdf

urlpatterns = [
    path("create/", OrderUser.as_view(), name="create_order"),
    path("history/pdf/", OrderHistoryPdf.as_view(), name='history_pdf'),
    path("payment/create/<int:order_id>/", create_payment, name="create_payment"),
    path("payment/callback/", liqpay_callback, name="liqpay_callback"),
]
