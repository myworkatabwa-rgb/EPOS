# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import json
import logging
from urllib.parse import parse_qs
from .models import Order, Customer, Product

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

        Order.objects.update_or_create(
            order_id=str(order_id),
            defaults={
                'customer': customer,
                'total': total,
                'status': status,
                'source': 'woocommerce'
            }
        )

        return JsonResponse({'success': True})

    except Exception as e:
        logger.exception("Error processing WooCommerce webhook")
        return JsonResponse({'success': False, 'error': str(e)})
