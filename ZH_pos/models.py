from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
import pandas as pd  # For CSV/Excel handling
import datetime

# =========================
# PRODUCT
# =========================
class Product(models.Model):
    # --- Basic Fields (your existing ones) ---
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    source = models.CharField(max_length=50, default="woocommerce")
    woo_id = models.IntegerField(null=True, blank=True, unique=True)

    # Extra fields for CSV/Excel import
    gtin = models.CharField(max_length=50, blank=True, null=True)
    upc = models.CharField(max_length=50, blank=True, null=True)
    ean = models.CharField(max_length=50, blank=True, null=True)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    visibility_in_catalog = models.CharField(max_length=50, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    allow_customer_reviews = models.BooleanField(default=True)
    purchase_note = models.TextField(blank=True, null=True)
    shipping_class = models.CharField(max_length=100, blank=True, null=True)
    swatches_attributes = models.TextField(blank=True, null=True)
    brands = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def import_from_file(cls, file_path):
        """
        Import products from CSV or Excel.
        Updates existing products by SKU if found, else creates new.
        """
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            product_data = {
                "sku": row.get("SKU"),
                "name": row.get("Name"),
                "price": row.get("Regular price") or row.get("Sale price") or 0,
                "stock": row.get("Stock") or 0,
                "gtin": row.get("GTIN"),
                "upc": row.get("UPC"),
                "ean": row.get("EAN"),
                "isbn": row.get("ISBN"),
                "published": row.get("Published") == "yes",
                "is_featured": row.get("Is featured?") == "yes",
                "visibility_in_catalog": row.get("Visibility in catalog"),
                "short_description": row.get("Short description"),
                "description": row.get("Description"),
                "sale_price": row.get("Sale price"),
                "regular_price": row.get("Regular price"),
                "categories": row.get("Categories"),
                "tags": row.get("Tags"),
                "weight": row.get("Weight (kg)"),
                "length": row.get("Length (cm)"),
                "width": row.get("Width (cm)"),
                "height": row.get("Height (cm)"),
                "allow_customer_reviews": row.get("Allow customer reviews?") == "yes",
                "purchase_note": row.get("Purchase note"),
                "shipping_class": row.get("Shipping class"),
                "swatches_attributes": row.get("Swatches Attributes"),
                "brands": row.get("Brands"),
            }

            if product_data["sku"]:
                obj, created = cls.objects.update_or_create(
                    sku=product_data["sku"],
                    defaults=product_data
                )
            else:
                # Create product without SKU
                obj = cls.objects.create(**product_data)

# =========================
# CUSTOMER
# =========================
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


# =========================
# ORDER
# =========================
class Order(models.Model):
    PAYMENT_CHOICES = (
        ("cash", "Cash"),
        ("card", "Card"),
        ("split", "Split"),
        ("bank", "Bank"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cash")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    source = models.CharField(max_length=50, default="pos")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

# =========================
# PACKING
# =========================
class Packing(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="packing"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    packed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Packing for {self.order.order_id}"


# =========================
# ORDER ITEM
# =========================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    woo_product_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


# =========================
# RETURN
# =========================
class Return(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return for {self.order.order_id}"


# =========================
# CASHIER
# =========================
class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
