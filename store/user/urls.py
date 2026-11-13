from django.urls import path


from user.views import (
    UserRegistration,
    UserProfile,
    UserAuthorization,
    logout_view,
    telegram_start,
    telegram_check,
    telegram_link_start,
    google_login,
)

urlpatterns = [
    path("profile/", UserProfile.as_view(), name="profile"),
    path("registration/", UserRegistration.as_view(), name="registration"),
    path("authorization/", UserAuthorization.as_view(), name="authorization"),
    path("logout/", logout_view, name="logout"),
    path("google/login/", google_login, name="google_login"),
    path("telegram/start/", telegram_start, name="telegram_start"),
    path("telegram/link/", telegram_link_start, name="telegram_link_start"),
    path("telegram/check/", telegram_check, name="telegram_check"),
]
