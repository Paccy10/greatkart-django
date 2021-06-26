from django import forms
from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phone_number', 'email', 'address_line_1',
                  'address_line_2', 'country', 'state', 'city', 'order_note']
