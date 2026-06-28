from django.urls import path

from preferences.views import set_theme, accept_cookies

urlpatterns = [

    path("theme/<str:theme>/", set_theme, name="set_theme"),
    path("accept-cookies/", accept_cookies, name="accept_cookies"),


]
