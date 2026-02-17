from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Customer, Order, OrderItem, Category

# Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock", "source", "category_list")
    search_fields = ("name", "sku")
    list_filter = ("source",)  # add CategoryFilter if ManyToMany

    def category_list(self, obj):
        """
        Returns the category names for display in admin.
        Handles both ForeignKey (obj.category) and ManyToMany (obj.categories) safely.
        """
        # ForeignKey case
        if hasattr(obj, "category") and obj.category:
            return obj.category.name

        # ManyToMany case, check it's a manager first
        if hasattr(obj, "categories") and obj.categories is not None:
            # Ensure it's a RelatedManager before calling exists()
            try:
                return ", ".join([c.name for c in obj.categories.all()])
            except AttributeError:
                return "-"

        return "-"
    category_list.short_description = "Category"

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
