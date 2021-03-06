from django.db import models
from django.db.models.aggregates import Avg, Count
from django.urls import reverse

from category.models import Category
from users.models import User


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

    def average_review(self):
        avg = 0
        reviews = ReviewRating.objects.filter(
            product=self, status=True).aggregate(average=Avg('rating'))

        if reviews['average'] is not None:
            avg = float(reviews['average'])

        return avg

    def count_reviews(self):
        count = 0
        reviews = ReviewRating.objects.filter(
            product=self, status=True).aggregate(count=Count('id'))

        if reviews['count'] is not None:
            count = int(reviews['count'])

        return count


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


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):

    product = models.ForeignKey(
        Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products')

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'

    def __str__(self):
        return self.product.name
