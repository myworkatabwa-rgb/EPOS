from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ZH_pos.models import (
    PhysicalStock, PhysicalStockItem,
    Product, Category, SubCategory, Branch
)


def generate_bill_no():
    last = PhysicalStock.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"{str(next_id).zfill(5)}/2Ab"


@login_required
def inventory(request):
    return render(request, "inventory/inventory.html")


@login_required
def physical_stock_list(request):
    stocks = PhysicalStock.objects.select_related("created_by", "branch").order_by("-created_at")
    return render(request, "inventory/physical_stock_list.html", {
        "stocks": stocks
    })


@login_required
def physical_stock_create(request):
    categories = Category.objects.filter(status=True).order_by("name")
    branches   = Branch.objects.all()
    bill_no    = generate_bill_no()
    today      = timezone.now().strftime("%d-%m-%Y")

    if request.method == "POST":
        try:
            data      = json.loads(request.body)
            date_str  = data.get("date")
            branch_id = data.get("branch_id") or None
            items     = data.get("items", [])

            from datetime import datetime
            date = datetime.strptime(date_str, "%d-%m-%Y").date()

            stock = PhysicalStock.objects.create(
                bill_no    = generate_bill_no(),
                date       = date,
                created_by = request.user,
                branch_id  = branch_id,
            )

            for item in items:
                product_id   = item.get("product_id")
                physical_qty = int(item.get("physical_qty") or 0)
                rate         = float(item.get("rate") or 0)
                batch_no     = item.get("batch_no", "")
                remarks      = item.get("remarks", "")

                if not product_id:
                    continue

                product    = Product.objects.get(id=product_id)
                system_qty = product.stock

                PhysicalStockItem.objects.create(
                    stock        = stock,
                    product_id   = product_id,
                    unit_name    = product.unit.Unit_name if product.unit else "Default",
                    batch_no     = batch_no,
                    system_qty   = system_qty,
                    physical_qty = physical_qty,
                    rate         = rate,
                    remarks      = remarks,
                )

                # Update product stock to physical count
                product.stock = physical_qty
                product.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/physical_stock_create.html", {
        "categories": categories,
        "branches":   branches,
        "bill_no":    bill_no,
        "today":      today,
    })


@login_required
def physical_stock_delete(request, stock_id):
    stock = get_object_or_404(PhysicalStock, id=stock_id)
    if request.method == "POST":
        stock.delete()
        messages.success(request, "Physical stock record deleted.")
    return redirect("physical_stock_list")


@login_required
def load_products_by_category(request):
    category_id    = request.GET.get("category_id")
    subcategory_id = request.GET.get("subcategory_id")
    sku            = request.GET.get("sku")

    products = Product.objects.filter(status="Active")

    if sku:
        products = products.filter(sku=sku)
    elif subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)
    elif category_id:
        products = products.filter(category_id=category_id)
    else:
        products = Product.objects.none()

    data = []
    for p in products:
        data.append({
            "id":    p.id,
            "name":  p.name,
            "sku":   p.sku or "—",
            "stock": p.stock,
            "rate":  float(p.price or 0),
            "unit":  p.unit.Unit_name if p.unit else "Default",
        })

    return JsonResponse(data, safe=False)
# views.py
@login_required
def physical_stock_detail(request, stock_id):
    stock = get_object_or_404(PhysicalStock, id=stock_id)
    items = stock.items.select_related("product", "product__unit").all()
    return render(request, "inventory/physical_stock_detail.html", {
        "stock": stock,
        "items": items,
    })


@login_required
def load_subcategories(request):
    category_id = request.GET.get("category_id")
    subs = SubCategory.objects.filter(category_id=category_id).values("id", "name")
    return JsonResponse(list(subs), safe=False)


@login_required
def stock_audit_form(request):
    return render(request, "inventory/stock_audit_form.html")


@login_required
def item_conversion(request):
    return render(request, "inventory/item_conversion.html")


@login_required
def demand_sheet(request):
    return render(request, "inventory/demand_sheet.html")


@login_required
def purchase_order(request):
    return render(request, "inventory/purchase_order.html")


@login_required
def goods_receive_note(request):
    return render(request, "inventory/goods_receive_note.html")


@login_required
def goods_receive_return_note(request):
    return render(request, "inventory/goods_receive_return_note.html")


@login_required
def item_recipe(request):
    return render(request, "inventory/item_recipe.html")


@login_required
def transfer_out(request):
    return render(request, "inventory/transfer_out.html")


@login_required
def transfer_in(request):
    return render(request, "inventory/transfer_in.html")
