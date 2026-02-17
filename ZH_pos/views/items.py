from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from ZH_pos.models import Product, ModifierGroup, ModifierItem, Supplier, Brand, Discount, Color, Size, Unit, Promotion, PriceList,Tax,Item,PriceListItem
import csv
import json
from django.db.models import Q
import openpyxl
from django.contrib import messages
from ZH_pos.utils import generate_barcode_base64
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
            cleaned_row = {}
            for key, value in zip(headers, row):
                if isinstance(value, str):
                    cleaned_row[key] = value.strip()
                else:
                    cleaned_row[key] = value
            rows.append(cleaned_row)

    else:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    imported = 0
    skipped = 0

    # ---------- PROCESS ROWS ----------
    for row in rows:

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
            # WooCommerce compatible mapping
            regular_price = Decimal(
                row.get("regular_price")
                or row.get("regular price")
                or row.get("price")
                or 0
            )

            sale_price = Decimal(
                row.get("sale_price")
                or row.get("sale price")
                or 0
            )

            stock = int(
                row.get("stock")
                or row.get("qty")
                or row.get("quantity")
                or 0
            )

        except (InvalidOperation, ValueError, TypeError):
            skipped += 1
            continue

        Product.objects.update_or_create(
            sku=sku,
            defaults={
                "name": name,
                "regular_price": regular_price,   # ✅ main price
                "sale_price": sale_price,         # ✅ sale price
                "price": regular_price,           # fallback field
                "stock": stock,
                "source": "import",
                "woo_id": None,
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
def add_brand(request):

    if request.method == "POST":

        Brand.objects.create(
            brand_code=request.POST.get("brand_code"),
            brand_name=request.POST.get("brand_name"),
        )

        return redirect("brand_list")

    # Auto generate next code
    last = Brand.objects.order_by("-id").first()

    if last:
        next_code = str(int(last.brand_code) + 1).zfill(4)
    else:
        next_code = "0001"

    return render(request, "items/add_brand.html", {
        "next_code": next_code
    })


def brand_list(request):

    brands = Brand.objects.all().order_by("-id")

    return render(request, "items/brand_list.html", {
        "brands": brands
    })
@login_required
def delete_brand(request, id):

    brand = get_object_or_404(Brand, id=id)

    brand.delete()

    return redirect("brand_list")
@login_required
def edit_brand(request, id):

    brand = get_object_or_404(Brand, id=id)

    if request.method == "POST":

        brand.brand_code = request.POST.get("brand_code")
        brand.brand_name = request.POST.get("brand_name")

        brand.save()

        return redirect("brand_list")

    return render(request, "items/edit_brand.html", {
        "brand": brand
    })
@login_required
def search_items(request):

    barcode = request.GET.get("barcode")
    name = request.GET.get("name")
    category = request.GET.get("category")

    items = Product.objects.none()  # show nothing by default

    # only search if any filter used
    if barcode or name or (category and category != "All"):

        items = Product.objects.all()

        if barcode:
            items = items.filter(sku__icontains=barcode)

        if name:
            items = items.filter(name__icontains=name)

        if category and category != "All":
            items = items.filter(categories__icontains=category)

    context = {
        "items": items
    }

    return render(request, "items/search_items.html", context)


@login_required
def print_multiple_barcodes(request):
    return render(request, "items/print_multiple_barcodes.html")
@login_required
def barcode_search_api(request):

    barcode = request.GET.get("barcode")

    try:
        product = Product.objects.get(sku=barcode)

        data = {
            "success": True,
            "id": product.id,
            "barcode": product.sku,
            "name": product.name,
            "price": str(product.sale_price or product.price or 0),
        }

    except Product.DoesNotExist:

        data = {
            "success": False
        }

    return JsonResponse(data)
@login_required
def generate_barcodes(request):

    data = json.loads(request.body)

    items = data.get("items", [])
    settings = data.get("settings", {})

    barcode_list = []

    for item in items:
        barcode_list.extend([item["barcode"]] * int(item["qty"]))

    request.session["barcode_list"] = barcode_list
    request.session["barcode_settings"] = settings

    return JsonResponse({
        "success": True,
        "url": "/items/barcode_preview/"
    })

@login_required
def barcode_preview(request):

    barcode_list = request.session.get("barcode_list", [])
    settings = request.session.get("barcode_settings", {})

    products = Product.objects.filter(sku__in=barcode_list)

    return render(request, "items/barcode_preview.html", {
        "items": products,
        "settings": settings,
        "store_name": "Orh WEAR"
    })

    
@login_required
def discount(request):
    if request.method == "POST":

        name = request.POST.get("name")
        value = request.POST.get("value")
        type = request.POST.get("type")
        status = request.POST.get("status")

        Discount.objects.create(
            name=name,
            value=value,
            type=type,
            status=status
        )

        return redirect("discount_list")
    return render(request, "items/discount.html")
@login_required
def discount_list(request):

    discounts = Discount.objects.all().order_by("-id")

    return render(request, "items/discount_list.html", {
        "discounts": discounts
    })


@login_required
def colors(request):

    # generate next code
    last = Color.objects.order_by("-id").first()
    next_code = f"{(last.id + 1) if last else 1:04d}"

    if request.method == "POST":

        color_name = request.POST.get("color_name")   # <-- lowercase

        if color_name:  # safety check
            last = Color.objects.order_by("-id").first()
            next_code = f"{(last.id + 1) if last else 1:04d}"

            Color.objects.create(
                Color_code=next_code,
                Color_name=color_name
            )

            return redirect("Color_list")

    return render(request, "items/colors.html", {"next_code": next_code})
@login_required
def search_products(request):
    q = request.GET.get("q", "").strip()

    products = Product.objects.all().order_by("id")

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(sku__icontains=q)
        )

    products = products[:50]

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name or "",
            "barcode": p.sku or "",
            "unit": "",
            "rate": str(p.sale_price or p.price or 0)
        })

    return JsonResponse({"data": data})


@login_required
def Color_list(request):
    colors = Color.objects.all().order_by("-id")
    return render(request, "items/colors_list.html", {"colors": colors})


@login_required
def delete_Color(request, id):
    color = get_object_or_404(Color, id=id)
    color.delete()
    return redirect("Color_list")


@login_required
def edit_Color(request, id):
    color = get_object_or_404(Color, id=id)

    if request.method == "POST":
        color.Color_code = request.POST.get("color_code")
        color.Color_name = request.POST.get("color_name")
        color.save()
        return redirect("Color_list")

    return render(request, "items/edit_color.html", {"color": color})


@login_required
def sizes(request):

    last = Size.objects.order_by("-id").first()
    next_code = f"{(last.id + 1) if last else 1:04d}"

    if request.method == "POST":
        size_name = request.POST.get("size_name")

        if size_name:  # prevent null error
            last = Size.objects.order_by("-id").first()
            next_code = f"{(last.id + 1) if last else 1:04d}"

            Size.objects.create(
                Size_code=next_code,
                Size_name=size_name
            )

            return redirect("Size_list")

    return render(request, "items/sizes.html", {"next_code": next_code})
@login_required
def Size_list(request):
    sizes = Size.objects.all().order_by("-id")
    return render(request, "items/sizes_list.html", {"sizes": sizes})


@login_required
def delete_Size(request, id):
    size = get_object_or_404(Size, id=id)
    size.delete()
    return redirect("Size_list")


@login_required
def edit_Size(request, id):
    size = get_object_or_404(Size, id=id)

    if request.method == "POST":
        size.Size_code = request.POST.get("Size_code")
        size.Size_name = request.POST.get("Size_name")
        size.save()
        return redirect("Size_list")

    return render(request, "items/edit_size.html", {"size": size})



@login_required
def units(request):

    last = Unit.objects.order_by("-id").first()
    next_code = f"{(last.id + 1) if last else 1:04d}"

    if request.method == "POST":
        unit_name = request.POST.get("unit_name")

        if unit_name:
            last = Unit.objects.order_by("-id").first()
            next_code = f"{(last.id + 1) if last else 1:04d}"

            Unit.objects.create(
                Unit_code=next_code,
                Unit_name=unit_name
            )

            return redirect("Unit_list")

    return render(request, "items/units.html", {"next_code": next_code})


# UNIT LIST
@login_required
def Unit_list(request):
    units = Unit.objects.all().order_by("-id")
    return render(request, "items/units_list.html", {"units": units})


# DELETE
@login_required
def delete_Unit(request, id):
    unit = get_object_or_404(Unit, id=id)
    unit.delete()
    return redirect("Unit_list")


# EDIT
@login_required
def edit_Unit(request, id):
    unit = get_object_or_404(Unit, id=id)

    if request.method == "POST":
        unit.Unit_code = request.POST.get("Unit_code")
        unit.Unit_name = request.POST.get("Unit_name")
        unit.save()
        return redirect("Unit_list")

    return render(request, "items/edit_unit.html", {"unit": unit})
@login_required
def promotions(request):
    return render(request, "items/promotions.html")


@login_required
def promotion_add(request):

    if request.method == "POST":

        promo_code = request.POST.get("promo_code")

        # ✅ Check duplicate promo code (case-insensitive)
        if Promotion.objects.filter(promo_code__iexact=promo_code).exists():
            messages.error(request, "Promo code already exists!")
            return redirect("items:promotion_add")   # use namespace if needed

        Promotion.objects.create(
            name=request.POST.get("name"),
            promo_code=promo_code,
            branch=request.POST.get("branch"),
            enable=request.POST.get("enable") == "Yes",
            from_date=request.POST.get("from_date") or None,
            to_date=request.POST.get("to_date") or None,
            days_applicable=request.POST.get("days"),
            priority=request.POST.get("priority") or 1,
            discount_type=request.POST.get("discount_type"),
            discount_value=request.POST.get("discount"),
            application=request.POST.get("application"),
        )

        messages.success(request, "Promotion added successfully!")
        return redirect("promotion_list") 

    return render(request, "items/promotion_add.html")


# LIST
@login_required
def promotion_list(request):
    promos = Promotion.objects.all().order_by("-id")
    return render(request, "items/promotion_list.html", {"promos": promos})


# DELETE
@login_required
def promotion_delete(request, id):
    promo = get_object_or_404(Promotion, id=id)
    promo.delete()
    return redirect("promotion_list")


# EDIT
@login_required
def promotion_edit(request, id):

    promo = get_object_or_404(Promotion, id=id)

    if request.method == "POST":
        promo.name = request.POST.get("name")
        promo.promo_code = request.POST.get("promo_code")
        promo.branch = request.POST.get("branch")
        promo.enable = request.POST.get("enable") == "Yes"
        promo.from_date = request.POST.get("from_date") or None
        promo.to_date = request.POST.get("to_date") or None
        promo.days_applicable = request.POST.get("days")
        promo.priority = request.POST.get("priority") or 1
        promo.discount_type = request.POST.get("discount_type")
        promo.discount_value = request.POST.get("discount")
        promo.application = request.POST.get("application")
        promo.save()

        return redirect("promotion_list")

    return render(request, "items/promotion_edit.html", {"promo": promo})


@login_required
def price_list(request):
    taxes = Tax.objects.all()
    units = Unit.objects.all()
    return render(request, "items/price-list.html", {
        "taxes": taxes,
        "units": units
    })



# REAL TIME BARCODE SEARCH
# REAL TIME BARCODE SEARCH
def get_item_by_barcode(request):
    barcode = request.GET.get('barcode')

    try:
        product = Product.objects.get(barcode__iexact=barcode.strip())

        return JsonResponse({
            "status": "found",
            "name": product.name,
            "id": product.id
        })

    except Product.DoesNotExist:
        return JsonResponse({"status": "not_found"})


# SAVE PRICE LIST
def save_price_list(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})

    try:
        data = json.loads(request.body)

        name = data.get("name")
        items = data.get("items", [])

        if not name:
            return JsonResponse({"success": False, "error": "Name missing"})

        pricelist = PriceList.objects.create(name=name)

        for row in items:

            item_id = row.get("item_id")
            if not item_id:
                continue

            try:
                item = Product.objects.get(id=item_id)
                unit = Unit.objects.get(id=row.get("unit"))
                tax = Tax.objects.get(id=row.get("tax"))
            except Exception as e:
                print("ROW ERROR:", e)
                continue

            price_value = float(row.get("price") or 0)

            PriceListItem.objects.update_or_create(
                pricelist=pricelist,
                item=item,
                defaults={
                    "unit": unit,
                    "price": price_value,
                    "tax": tax,
                    "price_inclusive": float(row.get("price_inclusive") or 0)
                }
            )

            # 🔥 ALSO UPDATE PRODUCT PRICE
            item.regular_price = price_value
            item.price = price_value
            item.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})




        return JsonResponse({"success": True})

    except Exception as e:
        print("SAVE ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)})
@login_required

def list_price_lists(request):

    price_lists = PriceList.objects.all().order_by("-id")

    return render(request, "price_list/list_price_lists.html", {
        "price_lists": price_lists
    })

@login_required
def price_list_detail(request, pk):

    price_list = get_object_or_404(PriceList, pk=pk)

    items = price_list.items.select_related(
        "product",
        "unit",
        "tax"
    )

    return render(request, "price_list/price_list_detail.html", {
        "price_list": price_list,
        "items": items
    })

@login_required
def bulk_update(request):
    return render(request, "items/bulk_update.html")

def get_categories_and_items(request):
    categories = Category.objects.all().values("id", "name")
    items = Product.objects.all().values(
        "id",
        "barcode",
        "name",
        "unit__name",
        "category__name",
        "sub_category__name",
        "purchase_rate",
        "sale_rate"
    )

    return JsonResponse({
        "categories": list(categories),
        "items": list(items)
    })



def get_filtered_data(request):
    type_selected = request.GET.get("type")
    id_selected = request.GET.get("id")

    if type_selected == "category":
        products = Product.objects.filter(category_id=id_selected)
    else:
        products = Product.objects.filter(id=id_selected)

    data = products.values(
        "id",
        "barcode",
        "name",
        "unit__name",
        "category__name",
        "sub_category__name",
        "purchase_rate",
        "sale_rate"
    )

    return JsonResponse({"data": list(data)})


@login_required
def price_checker(request):
    return render(request, "items/price_checker.html")


@login_required
def courier(request):
    return render(request, "items/courier.html")


@login_required
def sales_target(request):
    return render(request, "items/sales_target.html")
