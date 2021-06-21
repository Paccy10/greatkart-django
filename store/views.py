from django.shortcuts import render, get_object_or_404

from category.models import Category
from .models import Product


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(is_available=True, category=category)

    else:
        products = Product.objects.filter(is_available=True)

    context = {
        'products': products,
        'count': products.count()
    }

    return render(request, 'store/index.html', context)


def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as exception:
        raise exception

    context = {
        'product': product
    }

    return render(request, 'store/product_details.html', context)
