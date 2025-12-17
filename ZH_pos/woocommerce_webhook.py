# ZH_pos/webhooks.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def woocommerce_webhook(request):
    print("🔥🔥🔥 WEBHOOK HIT 🔥🔥🔥")
    print("METHOD:", request.method)
    print("HEADERS:", dict(request.headers))
    print("BODY:", request.body)

    return JsonResponse({"ok": True})
