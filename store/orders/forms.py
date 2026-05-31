from django import forms
from django.core.validators import RegexValidator

from orders.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('created', 'history', 'initiator')

        """
        forms.CharField = полный контроль поля
        mobile - поле, вынесли отдельно, и обработали через forms.CharField. Так как надо контролировать поведение,
            а именно:
            - валидацию
            - очистка  clean()
            - типы данных
                
        Meta.widgets = контроль только внешнего вида полей. Обычное отображение.
            - placeholder
            - readonly
            - style                                        
        """

        mobile = forms.CharField(
            validators=[
                RegexValidator(
                    regex=r'^\+380\d{9}$',
                    message='Введите номер в формате 675091213'
                )
            ],
            widget=forms.TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'XXXXXXXXXX'
            })
        )

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'readonly': 'readonly'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control mb-2'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control mb-2'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control mb-2'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control mb-2'
            }),
        }

#  валидируем поле mobile, и записываем его в бд, с префиксом +380

    def clean_mobile(self):
        return '+380' + self.cleaned_data['mobile']