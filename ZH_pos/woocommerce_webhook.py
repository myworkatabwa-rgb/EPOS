# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import json
import logging
from .models import Order, Customer, Product

logger = logging.getLogger(__name__)

@csrf_exempt
def woocommerce_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        # Decode JSON safely
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)} | Body: {request.body}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        logger.info(f"WooCommerce webhook payload: {data}")

        # Extract order info
        order_id = data.get('id')
        total_raw = data.get('total', '0')
        status = data.get('status', 'pending')
        billing = data.get('billing', {})

        # Convert total to Decimal safely
        try:
            total = Decimal(total_raw)
        except (InvalidOperation, TypeError):
            total = Decimal('0.00')

        # Get or create customer
        email = billing.get('email', '').strip()
        first_name = billing.get('first_name', '').strip()
        last_name = billing.get('last_name', '').strip()
        phone = billing.get('phone', '').strip()

        if not email:
            email = f"guest_{order_id}@example.com"  # fallback for missing email

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                'name': f"{first_name} {last_name}".strip(),
                'phone': phone
            }
        )

        # Create or update order
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
        # Always return 200 to WooCommerce, so it doesn’t retry endlessly
        return JsonResponse({'success': False, 'error': str(e)})
