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
def import_items(request):
    if request.method != "POST":
        return redirect(request.META.get('HTTP_REFERER', '/'))

    file = request.FILES.get("file")
    if not file:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    ext = file.name.split(".")[-1].lower()
    rows = []

    # ---------- READ FILE ----------
    if ext == "csv":
        content = file.read().decode("utf-8-sig")
        reader = csv.DictReader(content.splitlines())

        for row in reader:
            clean = {}
            for k, v in row.items():
                if k:
                    clean[
                        k.strip()
                        .lower()
                        .replace(" ", "_")
                        .replace("-", "_")
                    ] = v
            rows.append(clean)

    elif ext == "xlsx":
        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        headers = [
            str(cell.value)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            for cell in sheet[1]
        ]

        for r in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, r)))

    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # ---------- PROCESS ----------
    for row in rows:
        sku = str(
            row.get("barcode")
            or row.get("sku")
            or ""
        ).strip()

        name = str(row.get("name") or "").strip()

        if not sku or not name:
            continue

        price = Decimal(
            row.get("sale_rate")
            or row.get("price")
            or 0
        )

        stock = int(row.get("stock") or 0)

        Product.objects.update_or_create(
            sku=sku,
            defaults={
                "name": name,
                "price": price,
                "stock": stock,
                "source": "import",
                "woo_id": None,
            }
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))



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
