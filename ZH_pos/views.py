from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, Customer
import json
import uuid


def dashboard(request):
    orders = Order.objects.all().order_by('-created_at')[:5]
    products = Product.objects.all()
    customers = Customer.objects.all()[:5]

    return render(request, 'dashboard.html', {
        'orders': orders,
        'products': products,
        'customers': customers,
    })


@csrf_exempt
def pos_checkout(request):
    """
    Receives cart JSON from frontend and creates Order + Customer
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        cart = json.loads(request.body)

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        total = 0
        for item in cart.values():
            total += float(item["price"]) * int(item["qty"])

        # Create walk-in customer
        customer, _ = Customer.objects.get_or_create(
            name="Walk-in Customer",
            email=None
        )

        order = Order.objects.create(
            order_id=str(uuid.uuid4())[:8],
            customer=customer,
            total=total,
            status="completed",
            source="pos"
        )

        return JsonResponse({
            "success": True,
            "order_id": order.order_id,
            "total": total
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
