from django import forms

from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('created', 'history', 'initiator')

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'readonly': 'readonly',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Last name'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Address'
            })
        }
