# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import json
import logging
from .models import Order, Customer, Product, OrderItem

logger = logging.getLogger(__name__)

@csrf_exempt
def woocommerce_webhook(request):
    if request.method != "POST":
        return JsonResponse({"ok": True})

    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"Received Woo order: {data.get('id')}")

        # --- Extract order_id ---
        order_id = str(data.get("id"))
        if not order_id:
            logger.warning("No order id in webhook payload")
            return JsonResponse({"ok": True})

        # --- Customer ---
        billing = data.get("billing", {})
        email = billing.get("email") or f"guest_{order_id}@example.com"
        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                "phone": billing.get("phone","")
            }
        )

        # --- Order ---
        total = Decimal(data.get("total","0") or "0")
        order, _ = Order.objects.update_or_create(
            order_id=order_id,
            defaults={
                "customer": customer,
                "status": data.get("status","pending"),
                "total": total,
                "source": "woocommerce"
            }
        )

        # --- Line Items ---
        order.items.all().delete()
        for item in data.get("line_items", []):
            quantity = int(item.get("quantity",1))
            price = Decimal(item.get("price","0") or "0")
            try:
                total_item = Decimal(item.get("total","0") or str(price * quantity))
            except InvalidOperation:
                total_item = price * quantity

            # --- Match product ---
            product = None
            woo_product_id = item.get("product_id")
            sku = item.get("sku")
            if woo_product_id:
                product = Product.objects.filter(woo_id=woo_product_id).first()
            if not product and sku:
                product = Product.objects.filter(sku=sku).first()

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=item.get("name",""),
                woo_product_id=woo_product_id,
                quantity=quantity,
                price=price,
                total=total_item
            )

        logger.info(f"Order {order_id} saved with {len(data.get('line_items',[]))} items")
        return JsonResponse({"success": True})

    except Exception as e:
        logger.exception("Woo webhook error")
        return JsonResponse({"success": True})
