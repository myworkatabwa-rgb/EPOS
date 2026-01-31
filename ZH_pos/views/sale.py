from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from ZH_pos.models import Product
from datetime import date



from ZH_pos.models import Order


@login_required(login_url="/login/")
def sell(request):
    products = (
        Product.objects
        .filter(source="woocommerce")
        .order_by("name")
    )

    return render(request, "sales/sell.html", {
        "products": products
    })


@login_required(login_url="/login/")
def sale_history(request):
    sales = (
        Order.objects
        .select_related("customer")
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/sale_history.html",
        {"sales": sales}
    )


@login_required(login_url="/login/")
def sale_receipt(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_id=order_id
    )

    return JsonResponse({
        "bill": order.order_id,
        "date": order.created_at.strftime("%d-%m-%Y %I:%M %p"),
        "payment": order.payment_method,
        "customer": order.customer.name if order.customer else "Walk-in",
        "items": [
            {
                "name": item.product_name,
                "qty": item.quantity,
                "rate": float(item.price),
                "amount": float(item.total)
            }
            for item in order.items.all()
        ],
        "total": float(order.total),
    })

@permission_required("ZH_pos.delete_order", raise_exception=True)
def delete_sale(request, order_id):
    Order.objects.filter(order_id=order_id).delete()
    return redirect("/sales/history/")


@login_required(login_url="/login/")
def ecommerce_orders(request):
    orders = (
        Order.objects
        .filter(source="woocommerce")   # OR source="woocommerce"
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/ecommerce_orders.html",
        {"orders": orders}
    )


@login_required(login_url="/login/")
def advance_booking(request):
    products = (
        Product.objects
        .filter(source="woocommerce")
        .order_by("name")
    )

    return render(request, "sales/advance_booking.html", {

        "products": products,
        "bill_no": "Auto",
        "today": date.today()
    })

    
                 
@login_required(login_url="/login/")
def packing_slip(request):
    orders = (
        Order.objects
        .select_related("customer")
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/packing_slip.html",
        {
            "orders": orders
        }
    )

@login_required(login_url="/login/")
def packing_history(request):
    packings = (
        packing.objects
        .select_related("customer", "order")
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/packing_history.html",
        {
            "packings": packings
        }
    )




