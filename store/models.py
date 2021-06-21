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
