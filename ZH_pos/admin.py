from django.contrib import admin
from .models import Product, Customer, Order, OrderItem

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock', 'source')

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

# Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'price', 'total')
    can_delete = False

# Order Admin with Inline
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'total', 'status', 'source', 'created_at')
    inlines = [OrderItemInline]
