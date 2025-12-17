# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order

@csrf_exempt
def woocommerce_webhook(request):
    print("🔥 WEBHOOK HIT – DB TEST 🔥")

    Order.objects.create(
        order_id="TEST-ORDER-123",
        total=99.99,
        status="pending",
        source="woocommerce"
    )

    return JsonResponse({"ok": True})
