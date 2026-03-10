from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from ZH_pos.models import PhysicalStock, PhysicalStockItem, Product, Category, SubCategory, Branch, StockAudit, StockAuditItem, ItemConversion, ItemConversionIn, ItemConversionOut, DemandSheet, DemandSheetItem,PurchaseOrder, PurchaseOrderItem, Supplier, Product, Branch,DemandSheet, Category, SubCategory, GoodsReceiveNote, GoodsReceiveNoteItem,GRNReturnNote, GRNReturnNoteItem



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
    elif category_id == "all":
        pass  # return all active products
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




def generate_po_number():
    last = PurchaseOrder.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    today = timezone.now().strftime("%d%m%Y")
    return f"PO-{today}-{str(next_id).zfill(4)}"


# ── LIST ─────────────────────────────────────────────
@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.select_related(
        "supplier", "branch", "created_by"
    ).order_by("-created_at")
    return render(request, "inventory/purchase_order_list.html", {
        "orders": orders
    })


# ── CREATE ────────────────────────────────────────────
@login_required
def purchase_order_create(request):
    suppliers = Supplier.objects.filter(status__iexact="active").order_by("supplier_name")
    branches      = Branch.objects.all()
    categories    = Category.objects.filter(status=True).order_by("name")
    demand_sheets = DemandSheet.objects.order_by("-created_at")[:20]
    po_number     = generate_po_number()
    today         = timezone.now().strftime("%Y-%m-%d")

    if request.method == "POST":
        try:
            data          = json.loads(request.body)
            supplier_id   = data.get("supplier_id") or None
            branch_id     = data.get("branch_id") or None
            demand_id     = data.get("demand_sheet_id") or None
            expected_date = data.get("expected_date") or None
            notes         = data.get("notes", "")
            items         = data.get("items", [])

            if not items:
                return JsonResponse({"success": False, "error": "No items added."})

            total_amount = sum(
                float(i.get("rate", 0)) * int(i.get("ordered_qty", 0))
                for i in items
            )

            po = PurchaseOrder.objects.create(
                po_number      = generate_po_number(),
                supplier_id    = supplier_id,
                branch_id      = branch_id,
                demand_sheet_id = demand_id,
                expected_date  = expected_date,
                notes          = notes,
                total_amount   = total_amount,
                created_by     = request.user,
            )

            for item in items:
                product_id  = item.get("product_id")
                ordered_qty = int(item.get("ordered_qty", 0))
                rate        = float(item.get("rate", 0))

                if not product_id or ordered_qty <= 0:
                    continue

                product = Product.objects.get(id=product_id)

                PurchaseOrderItem.objects.create(
                    po_id       = po.id,
                    product_id  = product_id,
                    unit_name   = product.unit.Unit_name if product.unit else "Default",
                    ordered_qty = ordered_qty,
                    rate        = rate,
                    amount      = ordered_qty * rate,
                )

            return JsonResponse({"success": True, "id": po.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/purchase_order_create.html", {
        "suppliers":     suppliers,
        "branches":      branches,
        "categories":    categories,
        "demand_sheets": demand_sheets,
        "po_number":     po_number,
        "today":         today,
    })


# ── DETAIL ────────────────────────────────────────────
@login_required
def purchase_order_detail(request, pk):
    po    = get_object_or_404(PurchaseOrder, id=pk)
    items = po.items.select_related("product").all()
    return render(request, "inventory/purchase_order_detail.html", {
        "po":    po,
        "items": items,
    })


# ── RECEIVE ───────────────────────────────────────────
@login_required
def purchase_order_receive(request, pk):
    """Mark PO as received and update product stock"""
    po = get_object_or_404(PurchaseOrder, id=pk)

    if request.method == "POST":
        try:
            data         = json.loads(request.body)
            received_items = data.get("items", [])
            all_received = True

            for item_data in received_items:
                item_id      = item_data.get("item_id")
                received_qty = int(item_data.get("received_qty", 0))

                try:
                    item = PurchaseOrderItem.objects.get(id=item_id, po=po)
                    item.received_qty = received_qty
                    item.save()

                    # ✅ Update product stock
                    if item.product and received_qty > 0:
                        item.product.stock += received_qty
                        item.product.save()

                    if item.received_qty < item.ordered_qty:
                        all_received = False

                except PurchaseOrderItem.DoesNotExist:
                    continue

            # Update PO status
            po.status = "received" if all_received else "partial"
            po.save()

            return JsonResponse({"success": True, "status": po.status})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    items = po.items.select_related("product").all()
    return render(request, "inventory/purchase_order_receive.html", {
        "po":    po,
        "items": items,
    })


# ── DELETE ────────────────────────────────────────────
@login_required
def purchase_order_delete(request, pk):
    po = get_object_or_404(PurchaseOrder, id=pk)
    if request.method == "POST":
        if po.status == "received":
            messages.error(request, "Cannot delete a received purchase order.")
        else:
            po.delete()
            messages.success(request, "Purchase order deleted.")
    return redirect("purchase_order_list")


# ── LOAD DEMAND SHEET ITEMS ───────────────────────────
@login_required
def load_demand_sheet_items(request):
    demand_id = request.GET.get("demand_id")
    if not demand_id:
        return JsonResponse([], safe=False)

    try:
        demand = DemandSheet.objects.get(id=demand_id)
        items  = demand.items.select_related("product").all()
        data   = []
        for item in items:
            if item.product and item.requested_qty > 0:
                data.append({
                    "product_id":  item.product.id,
                    "name":        item.product.name,
                    "sku":         item.product.sku or "—",
                    "unit":        item.item_unit,
                    "ordered_qty": item.requested_qty,
                    "rate":        float(item.product.purchase_price or 0),
                    "stock":       item.product.stock,
                })
        return JsonResponse(data, safe=False)

    except DemandSheet.DoesNotExist:
        return JsonResponse([], safe=False)


# ── SEARCH PRODUCT FOR PO ─────────────────────────────
@login_required
def search_product_for_po(request):
    sku      = request.GET.get("sku", "").strip()
    name     = request.GET.get("name", "").strip()
    cat_id   = request.GET.get("category_id", "").strip()

    products = Product.objects.filter(status="Active")

    if sku:
        products = products.filter(sku__icontains=sku)
    elif name:
        products = products.filter(name__icontains=name)
    elif cat_id:
        products = products.filter(category_id=cat_id)
    else:
        return JsonResponse([], safe=False)

    data = [{
        "id":    p.id,
        "name":  p.name,
        "sku":   p.sku or "—",
        "unit":  p.unit.Unit_name if p.unit else "Default",
        "rate":  float(p.purchase_price or 0),
        "stock": p.stock,
    } for p in products[:20]]

    return JsonResponse(data, safe=False)

def generate_grn_number():
    from ZH_pos.models import GoodsReceiveNote
    last = GoodsReceiveNote.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"{str(next_id).zfill(5)}/2Ab"




@login_required
def grn_list(request):
    grns = GoodsReceiveNote.objects.select_related(
        "supplier", "branch", "created_by", "purchase_order"
    ).order_by("-created_at")
    return render(request, "inventory/goods-receive-note.html", {"grns": grns})


@login_required
def grn_create(request):
    suppliers = Supplier.objects.filter(status="Active").order_by("supplier_name")
    branches  = Branch.objects.all()
    pos       = PurchaseOrder.objects.filter(
        status__in=["pending", "partial"]
    ).order_by("-date")
    grn_no    = generate_grn_number()
    today     = timezone.now().strftime("%-d-%-m-%Y")

    if request.method == "POST":
        try:
            data           = json.loads(request.body)
            supplier_id    = data.get("supplier_id") or None
            po_id          = data.get("po_id") or None
            invoice_number = data.get("invoice_number", "")
            terms          = data.get("terms", "")
            description    = data.get("description", "")
            items          = data.get("items", [])

            if not items:
                return JsonResponse({"success": False, "error": "No items added."})

            total_amount = sum(float(i.get("amount", 0)) for i in items)

            grn = GoodsReceiveNote.objects.create(
                grn_no            = generate_grn_number(),
                supplier_id       = supplier_id,
                purchase_order_id = po_id,
                invoice_number    = invoice_number,
                terms             = terms,
                description       = description,
                total_amount      = total_amount,
                created_by        = request.user,
            )

            for item in items:
                product_id       = item.get("product_id")
                quantity         = int(item.get("quantity", 0))
                rate             = float(item.get("rate", 0))
                tax_percentage   = float(item.get("tax_percentage", 0))
                discount_percent = float(item.get("discount_percent", 0))
                batch_no         = item.get("batch_no", "")
                expiry           = item.get("expiry") or None
                po_qty           = int(item.get("po_qty", 0))
                po_no            = item.get("po_no", "")

                if not product_id or quantity <= 0:
                    continue

                product        = Product.objects.get(id=product_id)
                base_amount    = quantity * rate
                disc_amount    = base_amount * (discount_percent / 100)
                taxable_amount = base_amount - disc_amount
                tax_amount     = taxable_amount * (tax_percentage / 100)
                final_amount   = taxable_amount + tax_amount

                GoodsReceiveNoteItem.objects.create(
                    grn_id           = grn.id,
                    product_id       = product_id,
                    po_no            = po_no,
                    unit_name        = product.unit.Unit_name if product.unit else "Default",
                    batch_no         = batch_no,
                    expiry           = expiry,
                    po_qty           = po_qty,
                    quantity         = quantity,
                    rate             = rate,
                    amount           = final_amount,
                    tax_percentage   = tax_percentage,
                    tax_amount       = tax_amount,
                    discount_percent = discount_percent,
                )

                # ✅ Update stock
                product.stock += quantity
                product.save()

            return JsonResponse({"success": True, "id": grn.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/grn_create.html", {
        "suppliers": suppliers,
        "branches":  branches,
        "pos":       pos,
        "grn_no":    grn_no,
        "today":     today,
    })


@login_required
def grn_detail(request, pk):
    grn   = get_object_or_404(GoodsReceiveNote, id=pk)
    items = grn.items.select_related("product").all()
    return render(request, "inventory/grn_detail.html", {
        "grn":   grn,
        "items": items,
    })


@login_required
def grn_delete(request, pk):
    grn = get_object_or_404(GoodsReceiveNote, id=pk)
    if request.method == "POST":
        grn.delete()
        messages.success(request, "GRN deleted.")
    return redirect("grn_list")


@login_required
def load_po_items(request):
    po_id = request.GET.get("po_id")
    if not po_id:
        return JsonResponse([], safe=False)
    try:
        po    = PurchaseOrder.objects.get(id=po_id)
        items = po.items.select_related("product").all()
        data  = [{
            "product_id": i.product.id if i.product else None,
            "name":       i.product.name if i.product else "—",
            "sku":        i.product.sku if i.product else "—",
            "unit":       i.unit_name,
            "po_qty":     i.ordered_qty,
            "po_no":      po.po_number,
            "rate":       float(i.rate),
            "stock":      i.product.stock if i.product else 0,
        } for i in items]
        return JsonResponse(data, safe=False)
    except PurchaseOrder.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
def fetch_product_for_grn(request):
    sku = request.GET.get("sku", "").strip()
    if not sku:
        return JsonResponse({}, safe=False)
    try:
        p = Product.objects.get(sku=sku)
        return JsonResponse({
            "product_id": p.id,
            "name":       p.name,
            "sku":        p.sku,
            "unit":       p.unit.Unit_name if p.unit else "Default",
            "rate":       float(p.price or 0),
            "stock":      p.stock,
        })
    except Product.DoesNotExist:
        return JsonResponse({}, safe=False)

@login_required
def goods_receive_note(request):
    return render(request, "inventory/goods_receive_note.html")



def generate_return_no():
    last = GRNReturnNote.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"GRN-RET-{str(next_id).zfill(5)}"


@login_required
def goods_receive_return_note(request):
    suppliers = Supplier.objects.filter(status="Active").order_by("supplier_name")
    grns      = GoodsReceiveNote.objects.select_related("supplier").order_by("-created_at")[:30]
    return_no = generate_return_no()
    today     = timezone.now().strftime("%-d-%-m-%Y")

    if request.method == "POST":
        try:
            data        = json.loads(request.body)
            supplier_id = data.get("supplier_id") or None
            grn_id      = data.get("grn_id") or None
            reason      = data.get("reason", "")
            description = data.get("description", "")
            items       = data.get("items", [])

            if not items:
                return JsonResponse({"success": False, "error": "No items added."})

            total_amount = sum(float(i.get("amount", 0)) for i in items)

            ret = GRNReturnNote.objects.create(
                return_no    = generate_return_no(),
                supplier_id  = supplier_id,
                grn_id       = grn_id,
                reason       = reason,
                description  = description,
                total_amount = total_amount,
                created_by   = request.user,
            )

            for item in items:
                product_id       = item.get("product_id")
                return_qty       = int(item.get("return_qty", 0))
                rate             = float(item.get("rate", 0))
                tax_percentage   = float(item.get("tax_percentage", 0))
                discount_percent = float(item.get("discount_percent", 0))
                batch_no         = item.get("batch_no", "")
                expiry           = item.get("expiry") or None
                grn_qty          = int(item.get("grn_qty", 0))
                grn_no           = item.get("grn_no", "")
                item_reason      = item.get("reason", "")

                if not product_id or return_qty <= 0:
                    continue

                product        = Product.objects.get(id=product_id)
                base_amount    = return_qty * rate
                disc_amount    = base_amount * (discount_percent / 100)
                taxable_amount = base_amount - disc_amount
                tax_amount     = taxable_amount * (tax_percentage / 100)
                final_amount   = taxable_amount + tax_amount

                GRNReturnNoteItem.objects.create(
                    return_note_id   = ret.id,
                    product_id       = product_id,
                    grn_no           = grn_no,
                    unit_name        = product.unit.Unit_name if product.unit else "Default",
                    batch_no         = batch_no,
                    expiry           = expiry,
                    grn_qty          = grn_qty,
                    return_qty       = return_qty,
                    rate             = rate,
                    amount           = final_amount,
                    tax_percentage   = tax_percentage,
                    tax_amount       = tax_amount,
                    discount_percent = discount_percent,
                    reason           = item_reason,
                )

                # ✅ Deduct stock
                product.stock = max(0, product.stock - return_qty)
                product.save()

            return JsonResponse({"success": True, "id": ret.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "inventory/goods_receive_return_note.html", {
        "suppliers": suppliers,
        "grns":      grns,
        "return_no": return_no,
        "today":     today,
    })


@login_required
def grn_return_list(request):
    returns = GRNReturnNote.objects.select_related(
        "supplier", "grn", "created_by"
    ).order_by("-created_at")
    return render(request, "inventory/grn_return_list.html", {
        "returns": returns
    })


@login_required
def grn_return_detail(request, pk):
    ret   = get_object_or_404(GRNReturnNote, id=pk)
    items = ret.items.select_related("product").all()
    return render(request, "inventory/grn_return_detail.html", {
        "ret":   ret,
        "items": items,
    })


@login_required
def grn_return_delete(request, pk):
    ret = get_object_or_404(GRNReturnNote, id=pk)
    if request.method == "POST":
        ret.delete()
        messages.success(request, "GRN Return Note deleted.")
    return redirect("grn_return_list")


@login_required
def load_grn_items(request):
    grn_id = request.GET.get("grn_id")
    if not grn_id:
        return JsonResponse([], safe=False)
    try:
        grn   = GoodsReceiveNote.objects.get(id=grn_id)
        items = grn.items.select_related("product").all()
        data  = [{
            "product_id": i.product.id if i.product else None,
            "name":       i.product.name if i.product else "—",
            "sku":        i.product.sku if i.product else "—",
            "unit":       i.unit_name,
            "grn_qty":    i.quantity,
            "grn_no":     grn.grn_no,
            "batch_no":   i.batch_no or "",
            "expiry":     str(i.expiry) if i.expiry else "",
            "rate":       float(i.rate),
            "tax_percentage":   float(i.tax_percentage),
            "discount_percent": float(i.discount_percent),
            "stock":      i.product.stock if i.product else 0,
        } for i in items]
        return JsonResponse(data, safe=False)
    except GoodsReceiveNote.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
def item_recipe(request):
    return render(request, "inventory/item_recipe.html")


@login_required
def transfer_out(request):
    return render(request, "inventory/transfer_out.html")


@login_required
def transfer_in(request):
    return render(request, "inventory/transfer_in.html")
