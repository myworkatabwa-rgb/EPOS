import json
import uuid
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ZH_pos.models import Product, Order, OrderItem, Customer


@login_required(login_url="/login/")
def pos_view(request):
    products = Product.objects.all()
    return render(request, "pos.html", {"products": products})


@csrf_exempt
def pos_checkout(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        cart = data.get("cart", {})
        payment_method = data.get("payment_method", "cash")
        discount = Decimal(data.get("discount", 0))

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        customer, _ = Customer.objects.get_or_create(name="Walk-in Customer")

        order = Order.objects.create(
            order_id=str(uuid.uuid4())[:8],
            customer=customer,
            discount=discount,
            payment_method=payment_method,
            status="completed",
            source="pos"
        )

        total = Decimal(0)

        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            qty = int(item["qty"])

            if product.stock < qty:
                return JsonResponse(
                    {"error": f"Insufficient stock for {product.name}"},
                    status=400
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                woo_product_id=product.woo_id,
                quantity=qty,
                price=product.price
            )

            product.stock -= qty
            product.save()
            total += product.price * qty

        order.total = total - discount
        order.save()

        return JsonResponse({
            "success": True,
            "order_id": order.order_id,
            "total": float(order.total),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
