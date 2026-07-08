from django.contrib import admin

from products.models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "name", "quantity", "price")


admin.site.register(Product, ProductAdmin)
