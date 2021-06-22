from django.db import models
from django.urls import reverse

from category.models import Category


class Product(models.Model):

    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.FloatField()
    images = models.ImageField(upload_to='images/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])


variation_category_choices = (
    ('Color', 'Color'),
    ('Size', 'Size'),
)


class Variation(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=variation_category_choices)

    def __str__(self):
        return self.name


class ProductVariation(models.Model):

    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.value
