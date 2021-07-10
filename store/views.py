from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from orders.models import OrderProduct
from .models import Product, ProductGallery, ReviewRating
from .forms import ReviewForm


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(is_available=True, category=category)

    else:
        products = Product.objects.filter(is_available=True).order_by('-id')

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'count': products.count()
    }

    return render(request, 'store/index.html', context)


def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=product).exists()
    except Exception as exception:
        raise exception

    try:
        if request.user.is_authenticated:
            order_product = OrderProduct.objects.filter(
                user=request.user, product=product).exists()
        else:
            order_product = None
    except OrderProduct.DoesNotExist:
        order_product = None

    reviews = ReviewRating.objects.filter(product=product, status=True)

    product_gallery = ProductGallery.objects.filter(product=product)

    context = {
        'product': product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery
    }

    return render(request, 'store/product_details.html', context)


def search(request):
    products = None
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=query) | Q(name__icontains=query))

    context = {
        'products': products,
        'count': products.count()
    }

    return render(request, 'store/index.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(
                user=request.user, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(
                request, 'Thank you! Your review has been updated successfully')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)

            if form.is_valid():
                review = ReviewRating()
                review.subject = form.cleaned_data['subject']
                review.rating = form.cleaned_data['rating']
                review.review = form.cleaned_data['review']
                review.user = request.user
                review.product_id = product_id
                review.ip = request.META.get('REMOTE_ADDR')
                review.save()

                messages.success(
                    request, 'Thank you! Your review has been submitted successfully')
                return redirect(url)
