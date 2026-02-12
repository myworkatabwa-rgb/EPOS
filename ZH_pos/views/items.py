from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from ZH_pos.models import Product, ModifierGroup, ModifierItem
import csv
import json
import openpyxl
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


@login_required
def list_items(request):
    products = Product.objects.all().order_by("id")
    return render(
        request,
        "items/list_items.html",
        {
            "items": products  # keep template unchanged
        }
    )
@csrf_exempt
@login_required
@require_POST
def import_items(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    ext = file.name.split('.')[-1].lower()
    rows = []

    # ---------- READ FILE ----------
    if ext == "csv":
        content = file.read().decode("utf-8-sig")
        reader = csv.DictReader(content.splitlines())
        rows = [
            {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            for row in reader
        ]

    elif ext == "xlsx":
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        headers = [str(cell.value).strip().lower() for cell in sheet[1]]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))

    else:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    imported = 0
    skipped = 0

    for row in rows:
        # accept multiple possible column names
        sku = str(
            row.get("sku")
            or row.get("barcode")
            or row.get("product_code")
            or ""
        ).strip()

        name = str(
            row.get("name")
            or row.get("product")
            or row.get("item_name")
            or ""
        ).strip()

        if not sku or not name:
            skipped += 1
            continue

        try:
            price = Decimal(row.get("price") or row.get("sale_price") or 0)
            stock = int(row.get("stock") or row.get("qty") or 0)
        except Exception:
            skipped += 1
            continue

        Product.objects.update_or_create(
            sku=sku,
            defaults={
                "name": name,
                "price": price,
                "stock": stock,
                "source": "import",
                "woo_id": None,  # IMPORTANT (unique constraint)
            }
        )

        imported += 1

    return JsonResponse({
        "success": True,
        "imported": imported,
        "skipped": skipped,
        "total": len(rows),
    })



@require_POST
@login_required
def delete_items(request):
    ids = request.POST.getlist('ids')
    if ids:
        Product.objects.filter(id__in=ids).delete()

    # Redirect back to the page that submitted the form
    return redirect(request.META.get('HTTP_REFERER', '/'))



@login_required
def add_item(request):
    return render(request, "items/add_item.html")


# NEW VIEWS START HERE

@login_required
def item_modifiers(request):
    return render(request, "items/item_modifiers.html")


@login_required
def search_products(request):
    query = request.GET.get("q", "")

    if len(query) >= 3:
        items = Product.objects.filter(name__icontains=query).order_by("id")[:20]

        data = []
        for item in items:
            data.append({
                "id": item.id,
                "name": item.name,
                "sku": item.sku,
                "price": str(item.price),
            })

        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)

@login_required
def save_modifiers(request):

    if request.method == "POST":
        data = json.loads(request.body)

        modifier = ModifierGroup.objects.create(
            name=data["name"],
            is_count=data["is_count"],
            count=data["count"] or 0
        )

        for item in data["items"]:
            ModifierItem.objects.create(
                modifier=modifier,
                product_id=item["product_id"],
                amount=item["amount"],
                get_rate_from_modifier=item["get_rate"]
            )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})
@login_required
def modifiers_list(request):
    modifiers = ModifierGroup.objects.all().order_by("-id")
    return render(request, "items/modifiers_list.html", {
        "modifiers": modifiers
    })


@login_required
def suppliers(request):
    if request.method == "POST":
        Supplier.objects.create(
            supplier_code=request.POST.get("supplier_code"),
            supplier_name=request.POST.get("supplier_name"),
            phone=request.POST.get("phone"),
            fax=request.POST.get("fax"),
            mobile=request.POST.get("mobile"),
            city=request.POST.get("city"),
            country=request.POST.get("country"),
            status=request.POST.get("status"),
            email=request.POST.get("email"),
            ntn=request.POST.get("ntn"),
            strn=request.POST.get("strn"),
            cnic=request.POST.get("cnic"),
            address=request.POST.get("address"),
        )
        return redirect("supplier_list")

    return render(request, "items/suppliers.html")


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by("-id")
    return render(request, "items/supplier_list.html", {
        "suppliers": suppliers
    })

    


@login_required
def brands(request):
    return render(request, "items/brands.html")


@login_required
def search_item(request):
    return render(request, "items/search_item.html")


@login_required
def print_multiple_barcodes(request):
    return render(request, "items/print_multiple_barcodes.html")


@login_required
def discount(request):
    return render(request, "items/discount.html")


@login_required
def colors(request):
    return render(request, "items/colors.html")


@login_required
def sizes(request):
    return render(request, "items/sizes.html")


@login_required
def units(request):
    return render(request, "items/units.html")


@login_required
def promotions(request):
    return render(request, "items/promotions.html")


@login_required
def price_list(request):
    return render(request, "items/price_list.html")


@login_required
def bulk_update(request):
    return render(request, "items/bulk_update.html")


@login_required
def price_checker(request):
    return render(request, "items/price_checker.html")


@login_required
def courier(request):
    return render(request, "items/courier.html")


@login_required
def sales_target(request):
    return render(request, "items/sales_target.html")
