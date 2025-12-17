from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Customer, Order, OrderItem

# Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock", "source")

# Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")

# OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_link", "product_name", "quantity", "price", "total")
    can_delete = False

    def product_link(self, obj):
        if obj.product:
            url = f"/admin/{obj.product._meta.app_label}/{obj.product._meta.model_name}/{obj.product.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return obj.product_name
    product_link.short_description = "Product"

# Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "total", "status", "source", "created_at")
    inlines = [OrderItemInline]
