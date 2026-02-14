from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

# =========================
# PRODUCT
# =========================
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    source = models.CharField(max_length=50, default="woocommerce")
    woo_id = models.IntegerField(null=True, blank=True, unique=True)

    # Extra Woo / CSV fields
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


# =========================
# CUSTOMER
# =========================
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class ModifierGroup(models.Model):
    name = models.CharField(max_length=200)
    is_count = models.BooleanField(default=False)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ModifierItem(models.Model):
    modifier = models.ForeignKey(
        ModifierGroup,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    get_rate_from_modifier = models.BooleanField(default=False)

class Supplier(models.Model):

    supplier_code = models.CharField(max_length=50, blank=True, null=True)
    supplier_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    ntn = models.CharField(max_length=50, blank=True, null=True)
    strn = models.CharField(max_length=50, blank=True, null=True)
    cnic = models.CharField(max_length=50, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supplier_name
        
class Brand(models.Model):

    brand_code = models.CharField(max_length=50, unique=True)
    brand_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name
class Color(models.Model):

    Color_code = models.CharField(max_length=50, unique=True)
    Color_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Color_name
class Size(models.Model):

    Size_code = models.CharField(max_length=50, unique=True)
    Size_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Size_name

# =========================
# ORDER (SALE)
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

class Discount(models.Model):

    TYPE_CHOICES = (
        ("flat", "Flat"),
        ("percent", "Percent"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    name = models.CharField(max_length=100)

    value = models.DecimalField(max_digits=10, decimal_places=2)

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
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
# PACKING
# =========================
class Packing(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="packing")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    packed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Packing for {self.order.order_id}"


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
