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
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        # Handle JSON or form-encoded payload
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)} | Body: {request.body}")
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        elif request.content_type == 'application/x-www-form-urlencoded':
            body_str = request.body.decode('utf-8')
            parsed = parse_qs(body_str)
            data = {k: v[0] for k, v in parsed.items()}
        else:
            return JsonResponse({'error': 'Unsupported content type'}, status=400)

        logger.info(f"WooCommerce webhook payload: {data}")

        # Extract order info
        order_id = data.get('id') or data.get('webhook_id')
        total_raw = data.get('total', '0')
        status = data.get('status', 'pending')
        billing = data.get('billing', {})

        # Convert total to Decimal
        try:
            total = Decimal(total_raw)
        except (InvalidOperation, TypeError):
            total = Decimal('0.00')

        # Customer info
        email = billing.get('email', '').strip() if isinstance(billing, dict) else ''
        first_name = billing.get('first_name', '').strip() if isinstance(billing, dict) else ''
        last_name = billing.get('last_name', '').strip() if isinstance(billing, dict) else ''
        phone = billing.get('phone', '').strip() if isinstance(billing, dict) else ''

        if not email:
            email = f"guest_{order_id}@example.com"

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={'name': f"{first_name} {last_name}".strip(), 'phone': phone}
        )

        # Create or update order
        order_obj, _ = Order.objects.update_or_create(
            order_id=str(order_id),
            defaults={
                'customer': customer,
                'total': total,
                'status': status,
                'source': 'woocommerce'
            }
        )

        # Handle line items
        line_items = data.get('line_items', [])
        # Remove old items to avoid duplicates
        order_obj.items.all().delete()

        for item in line_items:
            product_name = item.get('name', '')
            woo_product_id = item.get('product_id')
            quantity = int(item.get('quantity', 1))
            try:
                price = Decimal(item.get('price', '0.00'))
            except (InvalidOperation, TypeError):
                price = Decimal('0.00')
            try:
                total_item = Decimal(item.get('total', '0.00'))
            except (InvalidOperation, TypeError):
                total_item = price * quantity

            # Link to Product if exists
            product_obj = None
            if woo_product_id:
                product_obj = Product.objects.filter(woo_id=woo_product_id).first()
                if product_obj:
                    # Optionally update price
                    product_obj.price = price
                    product_obj.save()

            OrderItem.objects.create(
                order=order_obj,
                product=product_obj,
                product_name=product_name,
                woo_product_id=woo_product_id,
                quantity=quantity,
                price=price,
                total=total_item
            )

        return JsonResponse({'success': True})

    except Exception as e:
        logger.exception("Error processing WooCommerce webhook")
        # Always return 200 to WooCommerce
        return JsonResponse({'success': False, 'error': str(e)})
