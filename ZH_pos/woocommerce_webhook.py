from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import json
import logging
from django.db import transaction

from .models import Order, Customer, Product, OrderItem, Category
from .woocommerce_api import get_wcapi

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
        sku = payload.get("sku")
        product = None

        # -------- Find product by SKU to avoid duplicates --------
        if sku:
            product = Product.objects.filter(sku=sku).first()

        if product:
            # Update existing product
            product.woo_id = woo_id
            product.name = payload.get("name", "")
            try:
                product.price = Decimal(payload.get("price") or "0")
            except InvalidOperation:
                product.price = Decimal("0")
            product.stock = payload.get("stock_quantity") or 0
            product.source = "woocommerce"
            product.save()
        else:
            # Create new product safely
            try:
                price = Decimal(payload.get("price") or "0")
            except InvalidOperation:
                price = Decimal("0")
            product = Product.objects.create(
                woo_id=woo_id,
                name=payload.get("name", ""),
                sku=sku,
                price=price,
                stock=payload.get("stock_quantity") or 0,
                source="woocommerce",
            )

        # -------- CATEGORY SYNC --------
        categories_data = payload.get("categories", [])
        category_instances = []

        for cat in categories_data:
            if cat and cat.get("id"):
                category_instance, _ = Category.objects.update_or_create(
                    woo_id=cat.get("id"),
                    defaults={
                        "name": cat.get("name", ""),
                        "status": True,
                    },
                )
                category_instances.append(category_instance)

        # Attach categories properly
        if hasattr(product, "categories"):
            product.categories.set(category_instances)
        elif category_instances:
            product.category = category_instances[0]
            product.save()

        logger.info(
            f"Upserted product {woo_id} with categories "
            f"{[c.name for c in category_instances]}"
        )
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

        # Save order items safely
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

                product_item = None
                if item.get("sku"):
                    product_item = Product.objects.filter(sku=item.get("sku")).first()

                OrderItem.objects.create(
                    order=order,
                    product=product_item,
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
# CATEGORY + PRODUCT SYNC
# =====================
def sync_woo_categories():
    """
    Sync products AND categories from WooCommerce properly.
    """
    wcapi = get_wcapi()
    if not wcapi:
        logger.warning("Skipping WooCommerce sync: API missing")
        return

    try:
        page = 1
        while True:
            response = wcapi.get("products", params={"per_page": 100, "page": page})
            if response.status_code != 200:
                logger.error(f"WooCommerce fetch failed: {response.status_code}")
                return

            products = response.json()
            if not products:
                break

            for p in products:
                # -------- CATEGORY SYNC --------
                categories_data = p.get("categories", [])
                category_instances = []
                for cat in categories_data:
                    if cat and cat.get("id"):
                        category_instance, _ = Category.objects.update_or_create(
                            woo_id=cat.get("id"),
                            defaults={
                                "name": cat.get("name", ""),
                                "status": True,
                            },
                        )
                        category_instances.append(category_instance)

                # -------- PRODUCT SYNC --------
                sku = p.get("sku")
                product = None

                if sku:
                    product = Product.objects.filter(sku=sku).first()

                if product:
                    # Update existing product
                    product.woo_id = p.get("id")
                    product.name = p.get("name", "")
                    try:
                        product.price = Decimal(p.get("price") or "0")
                    except InvalidOperation:
                        product.price = Decimal("0")
                    product.stock = p.get("stock_quantity") or 0
                    product.source = "woocommerce"
                    product.save()
                else:
                    try:
                        price = Decimal(p.get("price") or "0")
                    except InvalidOperation:
                        price = Decimal("0")
                    product = Product.objects.create(
                        woo_id=p.get("id"),
                        name=p.get("name", ""),
                        sku=sku,
                        price=price,
                        stock=p.get("stock_quantity") or 0,
                        source="woocommerce",
                    )

                # Attach categories properly
                if hasattr(product, "categories"):
                    product.categories.set(category_instances)
                elif category_instances:
                    product.category = category_instances[0]
                    product.save()

            page += 1

        logger.info("WooCommerce products and categories synced successfully")

    except Exception as e:
        logger.exception(f"Exception syncing WooCommerce data: {e}")
