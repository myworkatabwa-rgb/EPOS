from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from ZH_pos.models import Product, Packing, Category
from django.contrib import messages
from datetime import date
import uuid
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
        try:
            print("=== POST START ===")

            # SAFE data extraction
            cart_json = request.POST.get("cart_data", "[]")
            discount_raw = request.POST.get("discount", "0")
            customer_id = request.POST.get("customer_id", "")

            print(f"RAW DATA - cart: {cart_json[:100]}..., discount: {discount_raw}, customer: {customer_id}")

            # Parse JSON safely
            try:
                cart_items = json.loads(cart_json)
                print(f"PARSED {len(cart_items)} items")
            except Exception:
                print("JSON PARSE FAILED")
                return JsonResponse({'success': False, 'error': 'Invalid cart data'}, status=400)

            if not cart_items:
                print("EMPTY CART")
                return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)

            # Parse discount safely
            try:
                discount = float(discount_raw or 0)
            except Exception:
                discount = 0.0

            # Customer safely
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id)
                    print(f"Customer found: {customer}")
                except Customer.DoesNotExist:
                    print("Customer not found")
                    customer = None

            # DATABASE TRANSACTION
            with transaction.atomic():
                print("TRANSACTION START")

                # Generate order ID
                order_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
                print(f"Order ID: {order_id}")

                # Create ORDER
                order = Order.objects.create(
                    order_id=order_id,
                    customer=customer,
                    payment_method="cash",
                    status="pending",
                    source="booking",
                )
                print(f"Order created: {order.id}")

                # Process items SAFELY
                total_items = 0
                total_qty = 0
                sub_total = 0.0

                for item in cart_items[:10]:  # Limit to prevent crash
                    try:
                        pid = str(item.get("id"))
                        product = Product.objects.filter(id=pid).first()

                        if not product:
                            print(f"Product {pid} not found")
                            continue

                        qty = max(1, int(item.get("qty", 1)))
                        price = float(item.get("price", getattr(product, 'price', 0) or 0))

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

                    except Exception as item_error:
                        print(f"ITEM ERROR {item}: {item_error}")
                        continue

                # Update order totals
                net_amount = max(sub_total - discount, 0)
                order.total = net_amount
                order.discount = discount
                order.save()
                print(f"Order totals updated: {net_amount}")

                # Create Packing
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
                print(f"Packing created: {packing.booking_no}")

                print("=== SAVE SUCCESS ===")
                return JsonResponse({
                    'success': True,
                    'packing_no': packing.booking_no
                })

        except Exception as e:
            print(f"CRASH ERROR: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)

    # GET request - show form
    products = Product.objects.all().order_by("name")[:100]
    return render(request, "sales/packing_slip.html", {
        "products": products,
    })



@login_required(login_url="/login/")
def delete_booking(request, booking_no):
    packing = get_object_or_404(Packing, booking_no=booking_no)

    if request.method == "POST":
        packing.delete()
        messages.success(request, "Packing slip deleted.")
        return redirect("packing_his")  # ✅ Fixed: redirect after delete

    return redirect("packing_his")


@login_required(login_url="/login/")
def booking_detail(request, booking_no):
    packing = get_object_or_404(Packing, booking_no=booking_no)

    items = []
    sub_total = 0.0  # Use Decimal for precision

    for item in packing.items.all():
        amount = float(item.amount) if item.amount else 0.0
        items.append({
            "name": item.product.name,
            "qty": item.qty,
            "price": float(item.price),
            "amount": amount,  # Use stored amount, not recalculated
        })
        sub_total += amount

    # Use STORED database values instead of recalculating
    stored_discount = float(packing.discount or 0)
    stored_net_amount = float(packing.net_amount or 0)

    data = {
        "booking_no": packing.booking_no,
        "date": packing.created_at.strftime("%Y-%m-%d %H:%M"),
        "packed_by": packing.packed_by.username if packing.packed_by else "N/A",
        "customer": packing.customer.name if packing.customer else "Walk-in",
        "branch": getattr(packing, 'branch', 'Main Branch'),
        "sub_total": round(sub_total, 2),      # Round for display
        "discount": round(stored_discount, 2),
        "net_amount": round(stored_net_amount, 2),  # Use stored value
        "items": items,
    }

    print(f"DEBUG booking_detail: sub_total={sub_total}, discount={stored_discount}, net={stored_net_amount}")  # Debug
    return JsonResponse(data)


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