from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.contrib import messages

from ZH_pos.models import Order, OrderItem, Return


@login_required
def sale_returns(request):
    return render(request, "returns/sale_returns.html")


@login_required
def fetch_sale_for_return(request):
    bill_no = request.GET.get("bill_no", "").strip()
    invoice_no = request.GET.get("invoice_no", "").strip()

    if not bill_no and not invoice_no:
        return JsonResponse({"success": False, "error": "Please enter a Bill No or Invoice No"})

    try:
        order = None

        if bill_no:
            order = Order.objects.get(order_id=bill_no)  # ✅ Order uses order_id not bill_no
        elif invoice_no:
            order = Order.objects.get(order_id=invoice_no)

        items = []
        for item in order.items.all():  # ✅ related_name="items" on OrderItem
            items.append({
                "id": item.id,
                "barcode": item.product.sku if item.product else "—",
                "name": item.product_name,
                "qty": item.quantity,
                "price": float(item.price),
                "total": float(item.total),
            })

        return JsonResponse({
            "success": True,
            "sale_id": order.id,
            "bill_no": order.order_id,
            "items": items
        })

    except Order.DoesNotExist:
        return JsonResponse({"success": False, "error": "Order not found"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})



@login_required
def confirm_sale_return(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        sale_id = data["sale_id"]
        return_items = data["items"]

        # 👇 ADD THIS TEMPORARILY
        print("DEBUG return_items:", return_items)

        order = get_object_or_404(Order, id=sale_id)
        total_return_amount = 0

        for item in return_items:
            print("DEBUG item keys:", item.keys())  # 👈 see exact key names
            try:
                order_item = OrderItem.objects.get(id=item["sale_item_id"], order=order)
            except OrderItem.DoesNotExist:
                print("DEBUG: OrderItem not found for", item)  # 👈
                continue

            qty = int(item["qty"])
            print(f"DEBUG qty={qty}, order_item.quantity={order_item.quantity}")  # 👈
            if qty <= 0 or qty > order_item.quantity:
                print("DEBUG: qty check failed, skipping")  # 👈
                continue

            total_return_amount += qty * float(order_item.price)

        print("DEBUG total_return_amount:", total_return_amount)  # 👈


@login_required
def sale_return_history(request):
    returns = Return.objects.select_related("order").order_by("-created_at")
    return render(request, "returns/sale_return_history.html", {
        "returns": returns
    })
@login_required
def return_detail(request, return_id):
    ret = get_object_or_404(Return, id=return_id)
    
    # Get the original order items for this return
    items = []
    for item in ret.order.items.all():
        items.append({
            "name": item.product_name,
            "barcode": item.product.sku if item.product else "—",
            "qty": item.quantity,
            "price": float(item.price),
            "total": float(item.total),
        })

    return JsonResponse({
        "success": True,
        "id": ret.id,
        "order_id": ret.order.order_id,
        "customer": ret.order.customer.name if ret.order.customer else "Walk-in",
        "date": ret.created_at.strftime("%Y-%m-%d %H:%M"),
        "amount": float(ret.amount),
        "reason": ret.reason or "—",
        "items": items,
    })
# views.py — add this
@login_required
def delete_return(request, return_id):
    ret = get_object_or_404(Return, id=return_id)
    if request.method == "POST":
        ret.delete()
        messages.success(request, "Return deleted.")
    return redirect("sale_return_history")