import json
import uuid
from decimal import Decimal

from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required


from .models import Product, Order, OrderItem, Customer, Return
@login_required(login_url="/")
def pos_view(request):
    products = Product.objects.all()
    return render(request, "pos.html", {"products": products})


def dashboard(request):
    today = now().date()
    yesterday = today - timedelta(days=1)

    # ---- TODAY ----
    today_orders = Order.objects.filter(created_at__date=today)
    today_total = today_orders.aggregate(total=Sum("total"))["total"] or 0
    today_count = today_orders.count()

    # Payment split
    cash_sale = (
        today_orders.filter(payment_method="cash")
        .aggregate(total=Sum("total"))["total"] or 0
    )
    card_sale = (
        today_orders.filter(payment_method="card")
        .aggregate(total=Sum("total"))["total"] or 0
    )
    split_sale = (
        today_orders.filter(payment_method="split")
        .aggregate(total=Sum("total"))["total"] or 0
    )

    # ---- YESTERDAY ----
    yesterday_orders = Order.objects.filter(created_at__date=yesterday)
    yesterday_total = (
        yesterday_orders.aggregate(total=Sum("total"))["total"] or 0
    )

    # ---- ITEM WISE (LAST 30 DAYS) ----
    last_30 = now() - timedelta(days=30)
    item_sales = (
        OrderItem.objects
        .filter(order__created_at__gte=last_30)
        .values("product__name")
        .annotate(
            quantity=Sum("quantity"),
            amount=Sum("total")
        )
    )

    # ---- SALES CHART ----
    sales_chart = list (
        Order.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )

    context = {
        "today_total": today_total,
        "today_count": today_count,
        "cash_sale": cash_sale,
        "card_sale": card_sale,
        "split_sale": split_sale,
        "yesterday_total": yesterday_total,
        "item_sales": item_sales,
        "sales_chart": sales_chart,
    }

    return render(request, "dashboard.html", context)


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
        discount = float(data.get("discount", 0))

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        customer, _ = Customer.objects.get_or_create(
            name="Walk-in Customer"
        )

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

        total -= discount
        order.total = total
        order.save()

        return JsonResponse({
            "success": True,
            "order_id": order.order_id,
            "total": float(order.total),
            "payment_method": payment_method,
            "items": [
                {
                    "name": item.product.name if item.product else item.product_name,
                    "qty": item.quantity,
                    "price": float(item.price),
                    "total": float(item.total)
                }
                for item in order.items.all()
            ]
        })

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def process_return(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        order = Order.objects.get(order_id=order_id)
        amount = Decimal(request.POST.get("amount"))

        Return.objects.create(
            order=order,
            amount=amount
        )

        order.total -= amount
        order.save()

        return JsonResponse({"success": True})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
