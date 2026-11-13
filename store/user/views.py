import random
from datetime import timedelta

from django.contrib import auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.urls import reverse

from user.forms import (
    UserRegistrationForm,
    UserAuthorizationForm,
    TelegramUserConfirmCode,
)
from user.models import TelegramAuth, CustomUser, TelegramAuthPurpose
from user.utils import set_remember_me


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
            set_remember_me(request)
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
                set_remember_me(request)
                return HttpResponseRedirect(reverse("home"))
            else:
                form.add_error("password", "Incorrect username or password!")

            return render(request, self.template_path, {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")  # перенаправление на главную или куда угодно


"""Authentification with  Google + checkbox"""


def google_login(request):
    remember_me = request.POST.get("remember_me")

    request.session["remember_me"] = bool(remember_me)

    return redirect(reverse("social:begin", kwargs={"backend": "google-oauth2"}))


"""Authentification with  Telegram messenger"""


def generate_code():
    """Генерируем случайный шестизначный код и возвращает его в виде строки
    потому что это не число для математических вычислений, а идентификатор для поиска записи в базе данных."""
    return str(random.randint(100000, 999999))


def telegram_start(request):
    """Генерируем код, передаем его в форму, и создаём запись для последующей проверки Telegram-ботом,"""

    remember_me = request.GET.get("remember_me") == "true"
    request.session["remember_me"] = remember_me

    code = generate_code()
    TelegramAuth.objects.create(code=code)

    form = TelegramUserConfirmCode(initial={"code": code})
    return render(request, "user/telegram_wait.html", context={"form": form, "code": code})


@login_required
def telegram_link_start(request):
    """Создаёт код для привязки Telegram к аккаунту пользователя.
    Разрешаем привязку Telegram только авторизованным пользователям"""
    code = generate_code()

    TelegramAuth.objects.create(code=code, user=request.user, purpose=TelegramAuthPurpose.LINK)

    form = TelegramUserConfirmCode(initial={"code": code})

    return render(
        request,
        "user/telegram_wait.html",
        {"form": form, "code": code},
    )


def telegram_check(request):
    """Проверяем состояние операции с Telegram-кодом
    и в зависимости от результата либо подтверждает привязку, либо выполняет вход"""
    code = request.GET.get("code")

    obj = TelegramAuth.objects.filter(code=code).first()

    if not obj:
        return JsonResponse({"status": "pending"})

    if timezone.now() - obj.created_at > timedelta(minutes=1):
        return JsonResponse({"status": "expired"})

    if not obj.is_used or obj.telegram_id is None:
        return JsonResponse({"status": "pending"})

    # LINK - проверяет то, что только авторизованный пользователь может привязать Telegram
    if obj.purpose == TelegramAuthPurpose.LINK:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error"})

        if obj.user_id != request.user.pk:
            return JsonResponse({"status": "error"})

        return JsonResponse({"status": "linked"})

    # LOGIN - проверят, не вошёл ли пользователь другим способом, например через Google или email
    # Неавторизованный пользователь входит через уже привязанный Telegram
    elif obj.purpose == TelegramAuthPurpose.LOGIN:
        if request.user.is_authenticated:
            return JsonResponse({"status": "already_authenticated"})

        user = CustomUser.objects.filter(telegram_id=obj.telegram_id).first()

        if not user:
            return JsonResponse({"status": "error"})

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        remember_me = request.session.pop("remember_me", False)

        print("TELEGRAM REMEMBER ME:", repr(remember_me))

        set_remember_me(request, remember_me)

        print("SESSION EXPIRY AGE:", request.session.get_expiry_age())
        print("BROWSER CLOSE:", request.session.get_expire_at_browser_close())

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"})
