from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('categories/<slug:category_slug>/', views.store, name='products_by_category'),
    path('categories/<slug:category_slug>/<slug:product_slug>/',
         views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('submit-review/<int:product_id>/', views.submit_review, name='submit_review')
]
