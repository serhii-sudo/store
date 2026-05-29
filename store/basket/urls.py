from django.urls import path
from basket.views import AddInBasket, BasketView, DelBasket

urlpatterns = [
    path("add_to_cart/<int:product_id>/", AddInBasket.as_view(), name="add_to_cart"),
    path("user-basket/", BasketView.as_view(), name="user_basket"),
    path("del_cart/<int:id>/", DelBasket.as_view(), name="del_cart"),
]
