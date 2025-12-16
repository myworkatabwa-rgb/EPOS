from django.db import models
from decimal import Decimal

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)  # WooCommerce SKU optional
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    source = models.CharField(max_length=50, default='woocommerce')  # woo/shopify/offline
    woo_id = models.IntegerField(null=True, blank=True)  # WooCommerce product ID

    def __str__(self):
        return self.name


# Customer Model
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


# Order Model
class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    order_id = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    source = models.CharField(max_length=50, default='offline')  # woo/shopify/offline
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id


# OrderItem Model (stores products in each order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)  # Store product name in case Product deleted
    product_id = models.IntegerField(null=True, blank=True)  # WooCommerce product ID
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    # Optional: auto-calculate total if not set
    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.price * Decimal(self.quantity)
        super().save(*args, **kwargs)
