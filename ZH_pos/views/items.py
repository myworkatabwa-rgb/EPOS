from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from ZH_pos.models import Product
import csv
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
def suppliers(request):
    return render(request, "items/suppliers.html")


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
