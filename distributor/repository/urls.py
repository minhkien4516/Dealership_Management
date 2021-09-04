from django.urls import path
from . import views

urlpatterns = [
    path('product-importation/', views.product_importation_view, name='product-importation'),
    path('products-importation/', views.products_importation_view, name='products-importation'),
    path('product-exportation/', views.product_exportation_view, name='product-exportation'),
    path('products-exportation/', views.products_exportation_view, name='products-exportation'),
    path('products-report/', views.products_report_view, name='products-report'),
]
