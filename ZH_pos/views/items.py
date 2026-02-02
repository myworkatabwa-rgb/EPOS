from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ZH_pos.models import Product
import csv
import openpyxl
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
def import_items(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    ext = file.name.split('.')[-1].lower()

    if ext == "csv":
        rows = csv.DictReader(file.read().decode("utf-8").splitlines())

    elif ext == "xlsx":
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        rows = []
        headers = [cell.value for cell in sheet[1]]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))

    else:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    for row in rows:
        sku = str(row.get("sku")).strip()
        name = row.get("name")
        price = row.get("price") or 0
        stock = row.get("stock") or 0

        if not sku or not name:
            continue

        product, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                "name": name,
                "price": price,
                "stock": stock,
            }
        )

        if not created:
            # MERGE duplicate
            product.name = name
            product.price = price
            product.stock += int(stock)
            product.save()

    return JsonResponse({"success": True})


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
