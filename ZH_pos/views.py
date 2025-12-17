from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, OrderItem, Customer
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

def pos_view(request):
    products = Product.objects.all()
    return render(request, "pos.html", {"products": products})
@csrf_exempt
def pos_checkout(request):
    """
    POS checkout endpoint
    Receives cart JSON and creates Order + OrderItems
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        cart = json.loads(request.body)

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        # Walk-in customer
        customer, _ = Customer.objects.get_or_create(
            name="Walk-in Customer",
            email=None
        )

        total = 0

        order = Order.objects.create(
            order_id=str(uuid.uuid4())[:8],
            customer=customer,
            total=0,
            status="completed",
            source="pos"
        )

        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            qty = int(item["qty"])
            price = float(product.price)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=price
            )

            total += price * qty

        order.total = total
        order.save()

        return JsonResponse({
            "success": True,
            "order_id": order.order_id,
            "total": total
        })

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

