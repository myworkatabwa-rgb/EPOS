from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json

from ZH_pos.models import Order, OrderItem, Return


@login_required
def sale_returns(request):
    return render(request, "returns/sale_returns.html")


@login_required
def fetch_sale_for_return(request):
    """
    Fetch existing sale using bill_no OR invoice_no
    """
    bill_no = request.GET.get("bill_no")
    invoice_no = request.GET.get("invoice_no")

    try:
        sale = None

        if bill_no:
            sale = Sale.objects.get(bill_no=bill_no)
        elif invoice_no:
            sale = Sale.objects.get(invoice_no=invoice_no)

        items = []
        for item in sale.items.all():
            items.append({
                "id": item.id,
                "barcode": item.product.sku,
                "name": item.product.name,
                "qty": item.quantity,
                "price": float(item.price),
                "total": float(item.quantity * item.price),
            })

        return JsonResponse({
            "success": True,
            "sale_id": sale.id,
            "bill_no": sale.bill_no,
            "items": items
        })

    except sale.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Sale not found"
        })


@login_required
def confirm_sale_return(request):
    """
    Save Sale Return
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        sale_id = data["sale_id"]
        return_items = data["items"]

        sale = get_object_or_404(Sale, id=sale_id)

        sale_return = SaleReturn.objects.create(
            sale=sale,
            created_by=request.user
        )

        for item in return_items:
            sale_item = SaleItem.objects.get(id=item["sale_item_id"])

            qty = int(item["qty"])
            if qty <= 0 or qty > sale_item.quantity:
                continue

            SaleReturnItem.objects.create(
                sale_return=sale_return,
                product=sale_item.product,
                quantity=qty,
                price=sale_item.price
            )

            # reduce original sale qty
            sale_item.quantity -= qty
            sale_item.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def sale_return_history(request):
    returns = SaleReturn.objects.all().order_by("-id")
    return render(request, "returns/sale_return_history.html", {
        "returns": returns
    })
