from django.urls import path

from products.views import Home, GetAllProductsByCategories, ProductDetail

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("all_categories/<str:categories_name>/", GetAllProductsByCategories.as_view(), name="all_products"),
    path("product_detail/<int:id>/", ProductDetail.as_view(), name="product_detail"),
]
