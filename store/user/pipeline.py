from django.conf import settings


def apply_remember_me(strategy, *args, **kwargs):
    """Обработка checkbox Remember Me в формах. Работа с пользовательской сессией через Google"""
    request = strategy.request

    remember_me = request.session.pop("remember_me", False)

    print("PIPELINE REMEMBER ME:", repr(remember_me))

    if remember_me:
        request.session.set_expiry(settings.REMEMBER_ME_DURATION)
    else:
        request.session.set_expiry(0)

    print("SESSION EXPIRY AGE:", request.session.get_expiry_age())
    print("BROWSER CLOSE:", request.session.get_expire_at_browser_close())

    return {}
