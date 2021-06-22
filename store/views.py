from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from .models import Product


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

    context = {
        'product': product,
        'in_cart': in_cart
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
