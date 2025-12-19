from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ZH_pos.models import Order, Return


@csrf_exempt
def process_return(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        order = Order.objects.get(order_id=order_id)
        amount = Decimal(request.POST.get("amount"))

        Return.objects.create(order=order, amount=amount)

        order.total -= amount
        order.save()

        return JsonResponse({"success": True})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)
