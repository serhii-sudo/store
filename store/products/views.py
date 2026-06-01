from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views import View

from products.models import Product, Category


class Home(View):
    template_path = "products/home.html"

    def get(self, request):
        # Получаем строку поиска
        search_query = request.GET.get("search", "")

        # Получаем все категории
        category = Category.objects.all()

        # Фильтруем продукты, если есть поисковый запрос
        if search_query:
            product_all = Product.objects.filter(name__icontains=search_query).order_by("-created_at")
        else:
            product_all = Product.objects.all().order_by("-created_at")

        # Настройка пагинации
        paginator = Paginator(product_all, 8)
        page_number = request.GET.get("page")
        page_object = paginator.get_page(page_number)

        # Проверяем, есть ли товары
        no_products = not page_object

        # Отправляем данные в шаблон
        return render(
            request,
            self.template_path,
            {
                "category": category,
                "products": page_object,
                "search_query": search_query,  # Передаем строку поиска в контекст
                "no_products": no_products,  # Передаем флаг, если нет товаров
            },
        )


class GetAllProductsByCategories(View):
    template_path = "products/all_products.html"  # для отображения товаров по категориям

    def get(self, request, categories_name):
        category = get_object_or_404(Category, name=categories_name)

        product_all = Product.objects.filter(categories=category)

        paginator = Paginator(product_all, 8)
        page_number = request.GET.get("page")
        page_object = paginator.get_page(page_number)

        categories = Category.objects.all()

        return render(request, self.template_path, {"products": page_object, "category": categories})


class ProductDetail(View):
    template_path = "products/product_detail.html"

    def get(self, request, id):
        categories = Category.objects.all()
        product_detail = get_object_or_404(Product, id=id)
        return render(request, self.template_path, {"product_detail": product_detail, "category": categories})
