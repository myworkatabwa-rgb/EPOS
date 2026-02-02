from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
def import_items(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    ext = file.name.split(".")[-1].lower()

    # ---------- READ FILE ----------
    if ext == "csv":
        content = file.read().decode("utf-8-sig")
        reader = csv.DictReader(content.splitlines())
        rows = [{k.lower().strip(): v for k, v in row.items()} for row in reader]

    elif ext == "xlsx":
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        headers = [str(cell.value).strip().lower() for cell in sheet[1]]
        rows = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))

    else:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    created = 0
    updated = 0

    # ---------- PROCESS ROWS ----------
    for row in rows:
        print("IMPORT ROW:", row)  # DEBUG (watch terminal)

        sku = str(row.get("sku", "")).strip()
        name = str(row.get("name", "")).strip()

        if not sku or not name:
            print("SKIPPED: missing sku/name")
            continue

        # SAFE price
        try:
            price = Decimal(str(row.get("price", "0")).strip())
        except Exception as e:
            print("BAD PRICE:", e)
            price = Decimal("0.00")

        # SAFE stock
        try:
            stock = int(str(row.get("stock", "0")).strip())
        except Exception as e:
            print("BAD STOCK:", e)
            stock = 0

        product, was_created = Product.objects.update_or_create(
            sku=sku,
            defaults={
                "name": name,
                "price": price,
                "stock": stock,
            }
        )

        if was_created:
            created += 1
        else:
            updated += 1

    return JsonResponse({
        "success": True,
        "created": created,
        "updated": updated
    })


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
