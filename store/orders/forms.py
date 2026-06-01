from django import forms
from orders.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('created', 'history', 'initiator')


    # username (readonly)
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2',
            'readonly': 'readonly'
        })
    )

    # email
    email = forms.EmailField(
        required=True,
        max_length=150,
        min_length=5,
        widget=forms.EmailInput(attrs={
            'class': 'form-control mb-2'
        })
    )

    # first_name
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2'
        })
    )

    # last_name
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2'
        })
    )

    # address
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2'
        })
    )

    # mobile
    mobile = forms.CharField(required=True)

    # валидируем поле mobile, и записываем его в бд, с префиксом +380

    def clean_mobile(self):
        mobile = ''.join(self.cleaned_data['mobile'].split())

        if not mobile.isdigit() or len(mobile) != 9:
            raise forms.ValidationError('Номер должен содержать 9 цифр')

        return '+380' + mobile
