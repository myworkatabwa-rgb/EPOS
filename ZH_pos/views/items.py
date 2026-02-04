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
import csv
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product


@require_POST
def import_items(request):
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    try:
        decoded_file = uploaded_file.read().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(decoded_file)
    except Exception as e:
        return JsonResponse({"error": f"File read error: {str(e)}"}, status=400)

    imported = 0
    skipped = 0

    for row in reader:
        sku = row.get("sku")
        name = row.get("name")

        if not sku or not name:
            skipped += 1
            continue

        try:
            price = Decimal(row.get("price", "0"))
            stock = int(row.get("stock", 0))
        except Exception:
            skipped += 1
            continue

        Product.objects.update_or_create(
            sku=sku,
            defaults={
                "name": name,
                "price": price,
                "stock": stock,
                "source": "csv",
                "woo_id": None,
            }
        )

        imported += 1

    return JsonResponse({
        "success": True,
        "imported": imported,
        "skipped": skipped
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
