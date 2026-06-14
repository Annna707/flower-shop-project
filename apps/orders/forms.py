from decimal import Decimal

from django import forms

from .models import Order

DELIVERY_COSTS = {
    Order.DELIVERY_EXPRESS: Decimal('390.00'),
    Order.DELIVERY_STANDARD: Decimal('290.00'),
    Order.DELIVERY_PICKUP: Decimal('0.00'),
}


class OrderCreateForm(forms.Form):
    delivery_method = forms.ChoiceField(
        choices=Order.DELIVERY_CHOICES,
        label='Способ доставки',
        widget=forms.RadioSelect(attrs={'class': 'checkout-radio'}),
    )
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        label='Способ оплаты',
        widget=forms.RadioSelect(attrs={'class': 'checkout-radio'}),
    )
    first_name = forms.CharField(
        max_length=50,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (900) 123-45-67',
        }),
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        label='Город',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    address = forms.CharField(
        max_length=250,
        required=False,
        label='Адрес доставки',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Улица, дом, квартира',
        }),
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        label='Индекс',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Пожелания к букету, время доставки…',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')

        if delivery_method == Order.DELIVERY_PICKUP:
            cleaned_data.setdefault('city', 'Самовывоз')
            cleaned_data.setdefault('address', 'Салон ИМИДЖ, ул. Цветочная, 12')
        else:
            if not cleaned_data.get('city'):
                self.add_error('city', 'Укажите город доставки.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Укажите адрес доставки.')

        return cleaned_data

    def get_delivery_cost(self):
        method = self.cleaned_data.get('delivery_method', Order.DELIVERY_STANDARD)
        return DELIVERY_COSTS.get(method, Decimal('0.00'))
