from django.contrib import admin

from .models import Product, ProductVariation, Variation, ReviewRating


class ProductAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'price', 'stock',
                    'category', 'modified_date', 'is_available')


class ProductVariationAdmin(admin.ModelAdmin):
    model = ProductVariation()
    list_display = ('get_product', 'variation', 'value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('variation', 'value')

    def get_product(self, obj):
        return obj.variation.product

    get_product.short_description = 'Product'
    get_product.admin_order_field = 'variation__product'


class VariationAdmin(admin.ModelAdmin):

    list_display = ('product', 'name')


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
