from django.contrib import admin
from .models import Product, Customer, Order
from .models import OrderItem  # Uncomment or define OrderItem if you have it


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock', 'source')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')


# Inline for order items (ensure OrderItem is defined or imported)
class OrderItemInline(admin.TabularInline):
    model = OrderItem  # Replace with your actual OrderItem model
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('order_id', 'customer', 'total', 'status', 'source', 'created_at')
