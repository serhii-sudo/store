# set theme
from django.http import JsonResponse
from django.shortcuts import redirect


def set_theme(request, theme):
    response = redirect(request.META.get("HTTP_REFERER", "/"))

    if theme not in ("light", "pink"):
        theme = "light"

        # Сохраняем тему только после согласия
    if request.COOKIES.get("cookie_consent") == "accepted":
        response.set_cookie(
            "theme",
            theme,
            max_age=60 * 60 * 24 * 365,
        )

    return response

def accept_cookies(request):
    response = JsonResponse({"status": "ok"})
    response.set_cookie(
        "cookie_consent",
        "accepted",
        max_age=60 * 60 * 24 * 365,
    )
    return response