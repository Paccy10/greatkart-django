import json
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.core.mail import EmailMessage

from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from .utils import generate_order_number


def payments(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=body['orderID'])
        payment = Payment(
            user=request.user,
            payment_id=body['transactionID'],
            payment_method=body['paymentMethod'],
            amount_paid=body['amountPaid'],
            status=body['status']
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment
            order_product.user = request.user
            order_product.product = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()
            order_product.variations.set(item.variations.all())
            order_product.save()

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()

        mail_subject = 'Order Received'
        message = get_template('orders/order_received_email.html').render({
            'user': request.user,
            'order': order
        })
        send_email = EmailMessage(
            mail_subject, message, to=[request.user.email])
        send_email.content_subtype = 'html'
        send_email.send()

        data = {
            'order_number': order.order_number,
            'payment_id': payment.payment_id
        }

        return JsonResponse(data)

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


def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=payment_id)
        subtotal = 0
        for product in order_products:
            subtotal += product.product_price * product.quantity
        context = {
            'order': order,
            'order_products': order_products,
            'payment': payment,
            'subtotal': subtotal
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
