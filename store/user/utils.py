from django.conf import settings


def set_remember_me(request, remember_me=None):
    """Обработка Remember Me и управление сроком пользовательской сессии."""

    if remember_me is None:
        remember_me = request.POST.get("remember_me")

    if remember_me:
        request.session.set_expiry(settings.REMEMBER_ME_DURATION)
    else:
        request.session.set_expiry(0)

    print("REMEMBER ME:", remember_me)
    print("SESSION EXPIRY AGE:", request.session.get_expiry_age())
    print("BROWSER CLOSE:", request.session.get_expire_at_browser_close())
