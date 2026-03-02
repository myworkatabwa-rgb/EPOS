from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from ZH_pos.models import Product, Packing, Category
from django.contrib import messages
from datetime import date



from ZH_pos.models import Order


@login_required(login_url="/login/")
def sell(request):
    products = Product.objects.select_related("category").all().order_by("name")
    categories = Category.objects.all().order_by("name")

    return render(request, "sales/sell.html", {
        "products": products,
        "categories": categories,
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
    products = Product.objects.all().order_by("name")
    categories = Category.objects.all().order_by("name")

    return render(request, "sales/advance_booking.html", {

        "products": products,
        "categories": categories,
        "bill_no": "Auto",
        "today": date.today()
    })
    
                 
@login_required(login_url="/login/")
def packing_slip(request):

    if request.method == "POST":

        order = (
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product")
            .order_by("-created_at")
            .first()
        )

        if not order:
            messages.error(request, "No order found to create packing slip.")
            return redirect("packing_his")

        packing, created = Packing.objects.get_or_create(
            order=order,
            defaults={
                "customer": order.customer,
                "packed_by": request.user,
                "booking_no": f"PK-{order.id}"
            }
        )

        if created:

            total_items = 0
            total_qty = 0
            sub_total = 0

            for item in order.items.all():

                PackingItem.objects.create(
                    packing=packing,
                    product=item.product,
                    qty=item.qty,
                    price=item.price,
                    amount=item.qty * item.price
                )

                total_items += 1
                total_qty += item.qty
                sub_total += item.qty * item.price

            packing.total_items = total_items
            packing.total_qty = total_qty
            packing.net_amount = sub_total
            packing.save()

            messages.success(request, "Packing slip created successfully.")

        else:
            messages.warning(request, "Packing slip already exists.")

        return redirect("packing_his")

    products = Product.objects.all().order_by("name")

    return render(request, "sales/packing_slip.html", {"products": products})
@login_required(login_url="/login/")
def delete_booking(request, booking_no):
    packing = get_object_or_404(Packing, booking_no=booking_no)

    if request.method == "POST":
        packing.delete()
def booking_detail(request, booking_no):

    packing = get_object_or_404(Packing, booking_no=booking_no)

    items = []

    for item in packing.items.all():

        items.append({
            "name": item.product.name,
            "qty": item.qty,
            "price": float(item.price),
            "amount": float(item.amount),
        })

    data = {
        "booking_no": packing.booking_no,
        "date": packing.created_at.strftime("%Y-%m-%d %H:%M"),
        "packed_by": packing.packed_by.username if packing.packed_by else "",
        "customer": packing.customer.name if packing.customer else "Walk-in",
        "sub_total": float(packing.net_amount),
        "discount": float(packing.discount or 0),
        "net_amount": float(packing.net_amount),
        "items": items
    }

    return JsonResponse(data)

    return redirect("packing_his")
@login_required(login_url="/login/")
def packing_history(request):
    packings = (
        Packing.objects
        .select_related("customer", "order")
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/packing_history.html",
        {
            "bookings": packings  # ✅ match template
        }
    )


