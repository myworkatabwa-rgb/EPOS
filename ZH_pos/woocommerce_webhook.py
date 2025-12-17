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
        if data.get("type") in ["product.created", "product.updated", "product.deleted"]:
            woo_id = data.get("id")
            if data["type"] == "product.deleted":
                Product.objects.filter(woo_id=woo_id).delete()
                logger.info(f"Deleted Product {woo_id}")
                return JsonResponse({"success": True})
            
            # Create or update product
            product_data = data
            Product.objects.update_or_create(
                woo_id=woo_id,
                defaults={
                    "name": product_data.get("name", ""),
                    "sku": product_data.get("sku"),
                    "price": Decimal(product_data.get("price", "0.00")),
                    "stock": int(product_data.get("stock_quantity", 0)),
                    "source": "woocommerce",
                }
            )
            logger.info(f"Upserted Product {woo_id}")
            return JsonResponse({"success": True})

        # ---- Handle Order events ----
        if data.get("type") in ["order.created", "order.updated"]:
            order_id = str(data.get("id"))
            billing = data.get("billing", {})
            email = billing.get("email") or f"guest_{order_id}@example.com"
            customer, _ = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                    "phone": billing.get("phone", ""),
                }
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
                }
            )

            # Remove old items to avoid duplicates
            order_obj.items.all().delete()
            for item in data.get("line_items", []):
                quantity = int(item.get("quantity", 1))
                price = Decimal(item.get("price", "0.00"))
                total_item = Decimal(item.get("total", str(price * quantity)))

                product = None
                if item.get("sku"):
                    product = Product.objects.filter(sku=item.get("sku")).first()

                OrderItem.objects.create(
                    order=order_obj,
                    product=product,
                    product_name=item.get("name", ""),
                    woo_product_id=item.get("product_id"),
                    quantity=quantity,
                    price=price,
                    total=total_item
                )

            logger.info(f"Saved Order {order_id}")
            return JsonResponse({"success": True})

        # Unknown type
        return JsonResponse({"ok": True})

    except Exception as e:
        logger.exception("Woo webhook error")
        # Always return 200 so Woo retries succeed
        return JsonResponse({"success": True})
