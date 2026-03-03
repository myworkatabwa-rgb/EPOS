from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from ZH_pos.models import Product, Packing, Category
from django.contrib import messages
from datetime import date
import json
from django.db import transaction


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
        print("Post is received")
        cart_json = request.POST.get("cart_data", "[]")
        discount_raw = request.POST.get("discount", "0")
        customer_id = request.POST.get("customer_id") or None

        print("\n=== DEBUG POST ===")
        print("cart_data:", cart_json)
        print("==================\n")

        try:
            cart_items = json.loads(cart_json)
        except (json.JSONDecodeError, TypeError):
            cart_items = []

        if not cart_items:
            # For AJAX
            return JsonResponse({'success': False, 'error': 'Cart is empty. Please add items first.'}, status=400)

        try:
            discount = float(discount_raw)
        except (ValueError, TypeError):
            discount = 0.0

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                pass

        try:
            with transaction.atomic():
                import uuid
                order_id = "BK-" + uuid.uuid4().hex[:8].upper()

                # Fix: Use create_user_profile or defaults for required fields
                order = Order.objects.create(
                    order_id=order_id,
                    customer=customer,
                    created_by=request.user,  # Add if required (migrate first)
                    payment_method="cash",
                    status="pending",
                    source="booking",
                )

                total_items = 0
                total_qty = 0
                sub_total = 0.0

                product_cache = {}  # Fix loop performance
                for item in cart_items:
                    pid = item["id"]
                    if pid not in product_cache:
                        product_cache[pid] = Product.objects.get(id=pid)  # Use get() only once
                    product = product_cache[pid]
                    qty = int(item.get("qty", 1))
                    price = float(item.get("price", product.price or 0))

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=qty,
                        price=price,
                    )

                    total_items += 1
                    total_qty += qty
                    sub_total += qty * price

                net_amount = max(sub_total - discount, 0)
                order.total = net_amount
                order.discount = discount
                order.save()

                packing = Packing.objects.create(
                    order=order,
                    customer=customer,
                    packed_by=request.user,
                    booking_no=f"PK-{order_id}",
                    total_items=total_items,
                    total_qty=total_qty,
                    discount=discount,
                    net_amount=net_amount,
                )

                # Create PackingItem (cached products)
                for item in cart_items:
                    pid = item["id"]
                    product = product_cache[pid]
                    qty = int(item.get("qty", 1))
                    price = float(item.get("price", product.price or 0))
                    PackingItem.objects.create(
                        packing=packing,
                        product=product,
                        qty=qty,
                        price=price,
                        amount=qty * price,
                    )

            # Success for AJAX (no redirect)
            return JsonResponse({'success': True, 'packing_no': packing.booking_no})

        except Exception as e:
            print("SAVE ERROR:", e)  # Check server logs for exact error (e.g., IntegrityError)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # GET unchanged
    products = Product.objects.all().order_by("name")
    return render(request, "sales/packing_slip.html", {"products": products})



@login_required(login_url="/login/")
def delete_booking(request, booking_no):
    packing = get_object_or_404(Packing, booking_no=booking_no)

    if request.method == "POST":
        packing.delete()
        messages.success(request, "Packing slip deleted.")
        return redirect("packing_his")  # ✅ Fixed: redirect after delete

    return redirect("packing_his")


@login_required(login_url="/login/")  # ✅ Added login check
def booking_detail(request, booking_no):
    packing = get_object_or_404(Packing, booking_no=booking_no)

    items = []
    sub_total = 0  # ✅ Calculate real sub_total

    for item in packing.items.all():
        items.append({
            "name": item.product.name,
            "qty": item.qty,
            "price": float(item.price),
            "amount": float(item.amount),
        })
        sub_total += float(item.amount)  # ✅ Sum from items

    discount = float(packing.discount or 0)

    data = {
        "booking_no": packing.booking_no,
        "date": packing.created_at.strftime("%Y-%m-%d %H:%M"),
        "packed_by": packing.packed_by.username if packing.packed_by else "N/A",
        "customer": packing.customer.name if packing.customer else "Walk-in",
        "branch": getattr(packing, 'branch', 'Main Branch'),
        "sub_total": sub_total,          # ✅ Real sub total
        "discount": discount,
        "net_amount": sub_total - discount,  # ✅ Correct net
        "items": items,
    }

    return JsonResponse(data)  # ✅ Removed dead code below


@login_required(login_url="/login/")
def packing_history(request):
    packings = (
        Packing.objects
        .select_related("customer", "order", "packed_by")
        .order_by("-created_at")
    )
    
    print("\n=== PACKING HISTORY DEBUG ===")
    print("Total records:", packings.count())  # ✅ this is safe
    print("==============================\n")

    return render(request, "sales/packing_history.html", {"bookings": packings})