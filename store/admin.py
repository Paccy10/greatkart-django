from django.contrib import admin
import admin_thumbnails

from .models import Product, ProductVariation, Variation, ReviewRating, ProductGallery


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):

    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'price', 'stock',
                    'category', 'modified_date', 'is_available')
    inlines = [ProductGalleryInline]


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
admin.site.register(ProductGallery)
