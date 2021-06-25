import requests
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
from .forms import RegistrationForm
from .models import User


@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = User.objects.create_user(
                email=email,
                password=password,
                phone_number=phone_number,
                firstname=firstname,
                lastname=lastname,
                username=username
            )
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Account Activation'
            message = get_template('users/account_activation_email.html').render({
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.content_subtype = 'html'
            send_email.send()
            messages.success(
                request, 'User registered successfully! \
                Please check your email to activate your account')
            return redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)


@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    product_variations = []
                    product_quantities = []

                    for cart_item in cart_items:
                        variations = cart_item.variations.all()
                        product_variations.append(list(variations))
                        product_quantities.append(cart_item.quantity)

                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    items_ids = []

                    for item in cart_items:
                        ex_var_list.append(list(item.variations.all()))
                        items_ids.append(item.id)

                    for product_variation in product_variations:
                        if product_variation in ex_var_list:
                            index = ex_var_list.index(product_variation)
                            item_id = items_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += product_quantities[product_variations.index(
                                product_variation)]
                            item.user = user
                            item.save()
                        else:
                            item = CartItem.objects.get(cart=cart)
                            item.user = user
                            item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            url = request.META.get('HTTP_REFERER')

            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'users/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Congratulations! Your account is successfully activated')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'users/dashboard.html')


@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            user = User.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Password'
            message = get_template('users/reset_password_email.html').render({
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.content_subtype = 'html'
            send_email.send()
            messages.success(request, 'Link sent successfully! \
                Please check your email to continue')
            return redirect('forgot_password')
        else:
            messages.error(request, 'User with the given email does not exist')
            return redirect('forgot_password')

    return render(request, 'users/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'Invalid reset password link')
        return redirect('forgot_password')


@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
    return render(request, 'users/reset_password.html')
