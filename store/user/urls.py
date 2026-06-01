from django.urls import path

from user.views import UserRegistration, UserProfile, UserAuthorization, logout_view, telegram_start, telegram_check

urlpatterns = [
    path("profile/", UserProfile.as_view(), name="profile"),
    path("registration/", UserRegistration.as_view(), name="registration"),
    path("authorization/", UserAuthorization.as_view(), name="authorization"),
    path("logout/", logout_view, name="logout"),
    path("telegram/start/", telegram_start, name="telegram_start"),
    path("telegram/check/", telegram_check, name="telegram_check"),
]
