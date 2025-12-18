import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, OrderItem, Customer


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
    COMMERCIAL POS CHECKOUT
    Handles cart, stock, discount, and payment method
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)

        cart = data.get("cart", {})
        payment_method = data.get("payment_method", "cash")
        discount = float(data.get("discount", 0))

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        # Walk-in customer
        customer, _ = Customer.objects.get_or_create(name="Walk-in Customer")

        order = Order.objects.create(
            order_id=str(uuid.uuid4())[:8],
            customer=customer,
            total=0,
            discount=discount,
            payment_method=payment_method,
            status="completed",
            source="pos"
        )

        total = 0

        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            qty = int(item["qty"])

            if product.stock < qty:
                return JsonResponse({
                    "error": f"Insufficient stock for {product.name}"
                }, status=400)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )

            product.stock -= qty
            product.save()

            total += product.price * qty

        total -= discount
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
