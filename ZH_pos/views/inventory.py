from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ZH_pos.models import PhysicalStock, PhysicalStockItem, Product, Category, SubCategory, Branch, StockAudit, StockAuditItem, ItemConversion, ItemConversionIn, ItemConversionOut, DemandSheet, DemandSheetItem



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
def physical_stock_detail(request, pk):
    stock = get_object_or_404(PhysicalStock, id=pk)
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


def generate_audit_bill_no():
    last = StockAudit.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"{str(next_id).zfill(5)}/2Ab"


@login_required
def stock_audit_list(request):
    audits = StockAudit.objects.select_related("created_by", "branch").order_by("-date")
    return render(request, "inventory/stock_audit_list.html", {"audits": audits})


@login_required
def stock_audit_create(request):
    branches = Branch.objects.all()
    bill_no  = generate_audit_bill_no()
    today    = timezone.now().strftime("%d-%m-%Y")

    if request.method == "POST":
        try:
            data      = json.loads(request.body)
            items     = data.get("items", [])
            branch_id = data.get("branch_id") or None

            total_qty = sum(int(i.get("audited_qty", 0)) for i in items)

            audit = StockAudit.objects.create(
                bill_no    = generate_audit_bill_no(),
                created_by = request.user,
                branch_id  = branch_id,
                stock_qty  = len(items),
                total_qty  = total_qty,
            )

            for item in items:
                product_id   = item.get("product_id")
                audited_qty  = int(item.get("audited_qty", 0))
                rate         = float(item.get("rate", 0))
                if not product_id:
                    continue
                StockAuditItem.objects.create(
                    audit_id    = audit.id,
                    product_id  = product_id,
                    qty         = audited_qty,
                    rate        = rate,
                )

            return JsonResponse({"success": True, "audit_id": audit.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/stock_audit_create.html", {
        "branches": branches,
        "bill_no":  bill_no,
        "today":    today,
    })

@login_required
def stock_audit_detail(request, pk):
    audit = get_object_or_404(StockAudit, id=pk)
    items = audit.items.select_related("product").all()
    return render(request, "inventory/stock_audit_detail.html", {
        "audit": audit,
        "items": items,
    })


@login_required
def stock_audit_delete(request, pk):
    audit = get_object_or_404(StockAudit, id=pk)
    if request.method == "POST":
        audit.delete()
        messages.success(request, "Stock audit deleted.")
    return redirect("stock_audit_list")


@login_required
def fetch_product_by_barcode(request):
    sku = request.GET.get("sku", "").strip()
    if not sku:
        return JsonResponse({"success": False, "error": "No barcode provided"})
    try:
        product = Product.objects.get(sku=sku)
        return JsonResponse({
            "success":    True,
            "product_id": product.id,
            "name":       product.name,
            "sku":        product.sku,
            "rate":       float(product.price or 0),
            "system_qty": product.stock,  # ← current stock in DB
        })
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Product not found"})


def generate_conversion_bill_no():
    last = ItemConversion.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"{str(next_id).zfill(5)}/2Ab"


@login_required
def item_conversion_list(request):
    conversions = ItemConversion.objects.select_related(
        "created_by", "branch"
    ).order_by("-date")
    return render(request, "inventory/item_conversion_list.html", {
        "conversions": conversions
    })


@login_required
def item_conversion_create(request):
    bill_no = generate_conversion_bill_no()
    today   = timezone.now().strftime("%d-%m-%Y")

    if request.method == "POST":
        try:
            data            = json.loads(request.body)
            conversion_type = data.get("conversion_type", "positive")
            items_in        = data.get("items_in", [])
            items_out       = data.get("items_out", [])

            conversion = ItemConversion.objects.create(
                bill_no         = generate_conversion_bill_no(),
                created_by      = request.user,
                conversion_type = conversion_type,
            )

            # ── ADD stock for items_in ────────────────────────
            for item in items_in:
                product_id = item.get("product_id")
                quantity   = int(item.get("quantity", 0))
                if not product_id or quantity <= 0:
                    continue

                product = Product.objects.get(id=product_id)

                ItemConversionIn.objects.create(
                    conversion_id = conversion.id,
                    product_id    = product_id,
                    unit_name     = product.unit.Unit_name if product.unit else "Default",
                    quantity      = quantity,
                )

                # Add to stock
                product.stock += quantity
                product.save()

            # ── SUBTRACT stock for items_out ──────────────────
            for item in items_out:
                product_id = item.get("product_id")
                quantity   = int(item.get("quantity", 0))
                rate       = float(item.get("rate", 0))
                if not product_id or quantity <= 0:
                    continue

                product = Product.objects.get(id=product_id)

                ItemConversionOut.objects.create(
                    conversion_id = conversion.id,
                    product_id    = product_id,
                    unit_name     = product.unit.Unit_name if product.unit else "Default",
                    quantity      = quantity,
                    rate          = rate,
                )

                # Subtract from stock
                product.stock = max(0, product.stock - quantity)
                product.save()

            return JsonResponse({"success": True, "id": conversion.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/item_conversion_create.html", {
        "bill_no": bill_no,
        "today":   today,
    })


@login_required
def item_conversion_detail(request, pk):
    conversion = get_object_or_404(ItemConversion, id=pk)
    items_in   = conversion.items_in.select_related("product").all()
    items_out  = conversion.items_out.select_related("product").all()
    return render(request, "inventory/item_conversion_detail.html", {
        "conversion": conversion,
        "items_in":   items_in,
        "items_out":  items_out,
    })


@login_required
def item_conversion_delete(request, pk):
    conversion = get_object_or_404(ItemConversion, id=pk)
    if request.method == "POST":
        conversion.delete()
        messages.success(request, "Item conversion deleted.")
    return redirect("item_conversion_list")


@login_required
def search_product_for_conversion(request):
    sku  = request.GET.get("sku", "").strip()
    name = request.GET.get("name", "").strip()

    products = Product.objects.filter(status="Active")
    if sku:
        products = products.filter(sku__icontains=sku)
    elif name:
        products = products.filter(name__icontains=name)
    else:
        return JsonResponse([], safe=False)

    data = [{
        "id":       p.id,
        "name":     p.name,
        "sku":      p.sku or "—",
        "stock":    p.stock,
        "rate":     float(p.price or 0),
        "unit":     p.unit.Unit_name if p.unit else "Default",
    } for p in products[:20]]

    return JsonResponse(data, safe=False)

def generate_demand_no():
    from django.utils import timezone
    today = timezone.now().strftime("%d%m%Y")
    count = DemandSheet.objects.filter(
        demand_date=timezone.now().date()
    ).count() + 1
    return f"{today}{str(count).zfill(4)}"


@login_required
def demand_sheet_list(request):
    demands = DemandSheet.objects.select_related(
        "created_by", "branch"
    ).order_by("-created_at")
    return render(request, "inventory/demand_sheet_list.html", {
        "demands": demands
    })


@login_required
def demand_sheet_create(request):
    categories = Category.objects.filter(status=True).order_by("name")
    branches   = Branch.objects.all()
    demand_no  = generate_demand_no()
    today      = timezone.now().strftime("%-d-%-m-%Y")

    if request.method == "POST":
        try:
            data        = json.loads(request.body)
            description = data.get("description", "")
            from_date   = data.get("from_date") or None
            to_date     = data.get("to_date") or None
            branch_id   = data.get("branch_id") or None
            items       = data.get("items", [])

            demand = DemandSheet.objects.create(
                demand_no   = generate_demand_no(),
                created_by  = request.user,
                branch_id   = branch_id,
                description = description,
                from_date   = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else None,
                to_date     = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else None,
            )

            for item in items:
                product_id    = item.get("product_id")
                requested_qty = int(item.get("requested_qty", 0))
                consumption   = int(item.get("consumption", 0))
                remarks       = item.get("remarks", "")

                if not product_id:
                    continue

                product = Product.objects.get(id=product_id)

                DemandSheetItem.objects.create(
                    demand_id       = demand.id,
                    product_id      = product_id,
                    item_unit       = product.unit.Unit_name if product.unit else "Default",
                    requested_qty   = requested_qty,
                    available_stock = product.stock,
                    consumption     = consumption,
                    remarks         = remarks,
                )

            return JsonResponse({"success": True, "id": demand.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/demand_sheet_create.html", {
        "categories": categories,
        "branches":   branches,
        "demand_no":  demand_no,
        "today":      today,
    })


@login_required
def demand_sheet_detail(request, pk):
    demand = get_object_or_404(DemandSheet, id=pk)
    items  = demand.items.select_related("product").all()
    return render(request, "inventory/demand_sheet_detail.html", {
        "demand": demand,
        "items":  items,
    })


@login_required
def demand_sheet_delete(request, pk):
    demand = get_object_or_404(DemandSheet, id=pk)
    if request.method == "POST":
        demand.delete()
        messages.success(request, "Demand sheet deleted.")
    return redirect("demand_sheet_list")


@login_required
def load_consumption(request):
    """Load sales consumption between date range per product"""
    from_date = request.GET.get("from_date")
    to_date   = request.GET.get("to_date")

    if not from_date or not to_date:
        return JsonResponse([], safe=False)

    from django.db.models import Sum
    from ZH_pos.models import OrderItem

    consumption = OrderItem.objects.filter(
        order__created_at__date__gte=from_date,
        order__created_at__date__lte=to_date,
    ).values(
        "product_id",
        "product__name",
        "product__sku",
    ).annotate(total_sold=Sum("quantity"))

    data = [{
        "product_id":  c["product_id"],
        "name":        c["product__name"],
        "sku":         c["product__sku"] or "—",
        "consumption": c["total_sold"],
    } for c in consumption]

    return JsonResponse(data, safe=False)



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
