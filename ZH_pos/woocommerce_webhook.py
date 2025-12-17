# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import json
import logging
from urllib.parse import parse_qs
from .models import Order, Customer, Product, OrderItem

logger = logging.getLogger(__name__)

@csrf_exempt
def woocommerce_webhook(request):
    if request.method != "POST":
        return JsonResponse({"ok": True})

    try:
        # ---- Parse payload ----
        content_type = request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            data = json.loads(request.body.decode("utf-8"))
        else:
            parsed = parse_qs(request.body.decode("utf-8"))
            data = {k: v[0] for k, v in parsed.items()}

        logger.info(f"Incoming Woo payload: {data}")

        # ---- Handle Product events ----
        if "id" in data and ("sku" in data or "price" in data):
            # Detect product create/update
            woo_id = data.get("id")
            # Delete product if flagged
            if data.get("status") == "deleted" or data.get("type") == "product.deleted":
                Product.objects.filter(woo_id=woo_id).delete()
                logger.info(f"Deleted Product {woo_id}")
            else:
                # Create or update
                try:
                    price = Decimal(data.get("price", "0.00"))
                except (InvalidOperation, TypeError):
                    price = Decimal("0.00")
                Product.objects.update_or_create(
                    woo_id=woo_id,
                    defaults={
                        "name": data.get("name", ""),
                        "sku": data.get("sku"),
                        "price": price,
                        "stock": int(data.get("stock_quantity", 0)),
                        "source": "woocommerce",
                    },
                )
                logger.info(f"Upserted Product {woo_id}")

        # ---- Handle Order events ----
        if "id" in data and "line_items" in data:
            order_id = str(data.get("id"))
            billing = data.get("billing", {})
            email = billing.get("email") or f"guest_{order_id}@example.com"
            customer, _ = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                    "phone": billing.get("phone", ""),
                },
            )

            # Total
            try:
                total = Decimal(data.get("total", "0"))
            except (InvalidOperation, TypeError):
                total = Decimal("0.00")

            order_obj, _ = Order.objects.update_or_create(
                order_id=order_id,
                defaults={
                    "customer": customer,
                    "total": total,
                    "status": data.get("status", "pending"),
                    "source": "woocommerce",
                },
            )

            # Remove old items to avoid duplicates
            order_obj.items.all().delete()
            for item in data.get("line_items", []):
                quantity = int(item.get("quantity", 1))
                try:
                    price = Decimal(item.get("price", "0.00"))
                except (InvalidOperation, TypeError):
                    price = Decimal("0.00")
                try:
                    total_item = Decimal(item.get("total", str(price * quantity)))
                except (InvalidOperation, TypeError):
                    total_item = price * quantity

                product = None
                sku = item.get("sku")
                if sku:
                    product = Product.objects.filter(sku=sku).first()

                OrderItem.objects.create(
                    order=order_obj,
                    product=product,
                    product_name=item.get("name", ""),
                    woo_product_id=item.get("product_id"),
                    quantity=quantity,
                    price=price,
                    total=total_item,
                )

            logger.info(f"Saved Order {order_id}")

        # Always return 200 so WooCommerce considers it delivered
        return JsonResponse({"success": True})

    except Exception as e:
        logger.exception("Woo webhook error")
        return JsonResponse({"success": True})
