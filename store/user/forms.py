from django import forms
from django.contrib.auth.forms import UserCreationForm

from user.models import CustomUser

"""Почему разные  наследования в формах?
 UserCreationForm - (умеет проверять пароли (password1 и password2),
                  - валидировать совпадение
                  - хешировать пароль
 
 forms.Form - потому что логин — это не создание объекта в базе, просто проверка данных в базе(без class Meta: !!)
 """


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"})
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class UserAuthorizationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))



class TelegramUserConfirmCode(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"class": "form-control text-center", "readonly": "readonly"})
    )