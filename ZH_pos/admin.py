from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Customer, Order, OrderItem, Category

# =====================
# CATEGORY
# =====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "woo_id", "slug")  # show WooCommerce ID and slug if applicable
    search_fields = ("name", "slug")

# =====================
# PRODUCT
# =====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock", "source", "category_list")
    search_fields = ("name", "sku")
    list_filter = ("source", "category")  # filter by WooCommerce source and category

    def category_list(self, obj):
        # If your Product has a ForeignKey to Category
        if hasattr(obj, "category") and obj.category:
            return obj.category.name
        # If you use ManyToManyField (multiple categories)
        if hasattr(obj, "categories") and obj.categories.exists():
            return ", ".join([c.name for c in obj.categories.all()])
        return "-"
    category_list.short_description = "Category"

# =====================
# CUSTOMER
# =====================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")

# =====================
# ORDER ITEM INLINE
# =====================
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

# =====================
# ORDER
# =====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "total", "status", "source", "created_at")
    inlines = [OrderItemInline]
    search_fields = ("order_id", "customer__name", "customer__email")
    list_filter = ("status", "source")
