from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.name
# =========================


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
