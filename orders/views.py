from django.shortcuts import render, redirect

from carts.models import CartItem
from .forms import OrderForm
from .models import Order
from .utils import generate_order_number


def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() < 0:
        return redirect('store')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        tax = 0
        grand_total = 0

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax

        if form.is_valid():
            order = Order()
            order.user = current_user
            order.firstname = form.cleaned_data['firstname']
            order.lastname = form.cleaned_data['lastname']
            order.phone_number = form.cleaned_data['phone_number']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()
            order.order_number = generate_order_number(order)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'tax': tax
            }
            return render(request, 'orders/payments.html', context)

        else:
            return redirect('checkout')
