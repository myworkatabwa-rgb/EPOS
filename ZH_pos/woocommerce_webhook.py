# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
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
            data = json.loads(request.body.decode())
        else:
            parsed = parse_qs(request.body.decode())
            data = {k: v[0] for k, v in parsed.items()}

        logger.info(f"Woo payload received: {data}")

        # ---- Ignore test webhooks ----
        if "id" not in data:
            return JsonResponse({"ok": True})

        order_id = str(data["id"])

        # ---- Customer ----
        billing = data.get("billing", {})
        email = billing.get("email") or f"guest_{order_id}@example.com"

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                "phone": billing.get("phone", "")
            }
        )

        # ---- Order ----
        total = Decimal(data.get("total", "0"))
        order, _ = Order.objects.update_or_create(
            order_id=order_id,
            defaults={
                "customer": customer,
                "status": data.get("status", "pending"),
                "total": total,
                "source": "woocommerce"
            }
        )

        # ---- Order Items ----
        order.items.all().delete()  # remove old items to avoid duplicates
        for item in data.get("line_items", []):
            quantity = int(item.get("quantity", 1))
            price = Decimal(item.get("price", "0"))
            total_item = Decimal(item.get("total", str(price * quantity)))

            product = None
            sku = item.get("sku")
            if sku:
                product = Product.objects.filter(sku=sku).first()

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=item.get("name", ""),
                woo_product_id=item.get("product_id"),
                quantity=quantity,
                price=price,
                total=total_item
            )

        logger.info(f"Order {order_id} saved successfully")
        return JsonResponse({"success": True})

    except Exception as e:
        logger.exception("Woo webhook error")
        # Always return 200 to WooCommerce
        return JsonResponse({"success": True})
