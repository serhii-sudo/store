import random
from datetime import timedelta

from django.contrib import auth
from django.contrib.auth import login, logout

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.urls import reverse

from user.forms import UserRegistrationForm, UserAuthorizationForm, TelegramUserConfirmCode
from user.models import TelegramAuth, CustomUser


class UserProfile(View):
    template_path = "user/user_basket.html"

    def get(self, request):
        return render(request, self.template_path)


class UserRegistration(View):
    template_path = "user/registration.html"

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_path, {"form": form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # указали какой бэкенд использовать при ручной авторизации + важно для теста
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, self.template_path, {"form": form})


class UserAuthorization(View):
    template_path = "user/authorization.html"

    def get(self, request):
        form = UserAuthorizationForm()
        return render(request, self.template_path, {"form": form})

    def post(self, request):
        form = UserAuthorizationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")  # получение имени юзера
            password = form.cleaned_data.get("password")  # получение пароля юзера
            user = auth.authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))  # перенаправление в кабинет
            else:
                return render(
                    request, self.template_path, {"form": form, "error_message": "Неверное имя пользователя или пароль"}
                )
        else:
            form = UserRegistrationForm()
        return render(request, self.template_path, {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")  # перенаправление на главную или куда угодно


""" регистрация & авторизация через telegram messenger"""


# генерируем рандомные 6-значные коды
def generate_code():
    return str(random.randint(100000, 999999))


# перехватываем сгенерированный код и передаем его в форму
def telegram_start(request):
    code = generate_code()
    TelegramAuth.objects.create(code=code)

    form = TelegramUserConfirmCode(initial={"code": code})
    return render(request, "user/telegram_wait.html", context={"form": form, "code": code})


def telegram_check(request):
    code = request.GET.get("code")

    obj = TelegramAuth.objects.filter(code=code).first()

    if not obj:
        return JsonResponse({"status": "pending"})

    # проверка времени жизни кода авторизации(например 1 минуты)
    if timezone.now() - obj.created_at > timedelta(minutes=1):
        return JsonResponse({"status": "expired"})

    # проверяем чтобы telegram_id был не None,
    # таким образом запрещаем логинить до получения значения telegram_id
    # блокируем вход до тех пор, пока telegram_id не установлен ботом
    if not obj.telegram_id:
        return JsonResponse({"status": "pending"})

    user = CustomUser.objects.filter(telegram_id=obj.telegram_id).first()

    if not user:
        return JsonResponse({"status": "pending"})

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    return JsonResponse({"status": "ok"})
