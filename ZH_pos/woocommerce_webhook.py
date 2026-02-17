from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal, InvalidOperation
import json
import logging
import os

from .models import Order, Customer, Product, OrderItem, Category
from woocommerce import API
from django.db import transaction

logger = logging.getLogger(__name__)


# =====================
# WOOCOMMERCE WEBHOOK
# =====================
@csrf_exempt
def woocommerce_webhook(request):
    if request.method != "POST":
        return JsonResponse({"ok": True})

    if not request.body:
        logger.warning("Woo webhook received empty body")
        return JsonResponse({"ok": True})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON payload: {request.body}")
        return JsonResponse({"ok": True})

    resource = request.headers.get("X-WC-Webhook-Resource")
    event = request.headers.get("X-WC-Webhook-Event")

    logger.info(f"Woo webhook: {resource}.{event}")

    # =====================
    # PRODUCT WEBHOOKS
    # =====================
    if resource == "product":
        woo_id = payload.get("id")

        if event == "deleted":
            Product.objects.filter(woo_id=woo_id).delete()
            logger.info(f"Deleted product {woo_id}")
            return JsonResponse({"success": True})

        try:
            price = Decimal(payload.get("price") or "0")
        except InvalidOperation:
            price = Decimal("0")

        # CATEGORY SYNC
        category_instance = None
        categories_data = payload.get("categories", [])

        if categories_data:
            cat_data = categories_data[0]  # Take first category
            category_instance, _ = Category.objects.update_or_create(
                woo_id=cat_data.get("id"),
                defaults={
                    "name": cat_data.get("name"),
                    "slug": cat_data.get("slug"),
                },
            )

        # PRODUCT SAVE
        Product.objects.update_or_create(
            woo_id=woo_id,
            defaults={
                "name": payload.get("name", ""),
                "sku": payload.get("sku"),
                "price": price,
                "stock": payload.get("stock_quantity") or 0,
                "category": category_instance,
                "source": "woocommerce",
            },
        )

        logger.info(f"Upserted product {woo_id}")
        return JsonResponse({"success": True})

    # =====================
    # ORDER WEBHOOKS
    # =====================
    if resource == "order":
        order_id = str(payload.get("id"))
        billing = payload.get("billing", {})

        email = billing.get("email") or f"guest_{order_id}@example.com"

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                "phone": billing.get("phone", ""),
            },
        )

        try:
            total = Decimal(payload.get("total") or "0")
        except InvalidOperation:
            total = Decimal("0")

        order, _ = Order.objects.update_or_create(
            order_id=order_id,
            defaults={
                "customer": customer,
                "total": total,
                "status": payload.get("status", "pending"),
                "source": "woocommerce",
            },
        )

        # Use transaction for safety
        with transaction.atomic():
            order.items.all().delete()
            for item in payload.get("line_items", []):
                quantity = int(item.get("quantity", 1))

                try:
                    price = Decimal(item.get("price") or "0")
                except InvalidOperation:
                    price = Decimal("0")

                try:
                    total_item = Decimal(item.get("total") or price * quantity)
                except InvalidOperation:
                    total_item = price * quantity

                product = None
                if item.get("sku"):
                    product = Product.objects.filter(sku=item.get("sku")).first()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item.get("name", ""),
                    woo_product_id=item.get("product_id"),
                    quantity=quantity,
                    price=price,
                    total=total_item,
                )

        logger.info(f"Saved order {order_id}")
        return JsonResponse({"success": True})

    return JsonResponse({"ok": True})


# =====================
# CATEGORY SYNC UTILITY
# =====================
# =====================
# CATEGORY SYNC
# =====================
def sync_woo_categories():
    """
    Sync categories from WooCommerce safely.
    Will skip syncing if API credentials are missing or invalid.
    """
    wcapi = get_wcapi()
    if not wcapi:
        logger.warning("Skipping WooCommerce category sync because API is None or credentials missing.")
        return

    try:
        response = wcapi.get("products/categories")
    except Exception as e:
        logger.exception(f"Failed to connect to WooCommerce API: {e}")
        return

    if response is None:
        logger.warning("WooCommerce API returned None response.")
        return

    if response.status_code != 200:
        logger.error(f"Failed to fetch Woo categories: {response.status_code} {getattr(response, 'text', '')}")
        return

    try:
        categories = response.json()
    except Exception as e:
        logger.exception(f"Failed to parse WooCommerce categories JSON: {e}")
        return

    for cat in categories:
        try:
            Category.objects.update_or_create(
                woo_id=cat.get("id"),
                defaults={
                    "name": cat.get("name", ""),
                    "slug": cat.get("slug", ""),
                }
            )
        except Exception as e:
            logger.exception(f"Failed to update/create category {cat.get('name')}: {e}")

    logger.info("WooCommerce categories synced successfully")


# =====================
# CATEGORY VIEWS
# =====================
@login_required
def list_category(request):
    # Always sync before showing
    sync_woo_categories()

    categories = Category.objects.all()
    return render(request, "category/list_category.html", {"categories": categories})


@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        Category.objects.create(name=name)
        return redirect("list_category")

    return render(request, "category/add_category.html")
