from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ZH_pos.models import Category
from ZH_pos.woocommerce_webhook import sync_woo_categories
import logging

logger = logging.getLogger(__name__)


@login_required
def list_category(request):
    """
    List all categories and safely sync from WooCommerce.
    If WooCommerce API is not available or fails, page still works.
    """

    try:
        # 🔥 Call safe WooCommerce sync
        sync_woo_categories()
    except Exception as e:
        logger.error(f"Failed to sync WooCommerce categories: {e}")

    categories = Category.objects.all()

    return render(request, "categories/list_category.html", {
        "categories": categories
    })
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status") == "on"

        if not name:
            messages.error(request, "Category name is required.")
            return redirect("list_category")

        if Category.objects.exclude(id=category_id).filter(name=name).exists():
            messages.error(request, "A category with this name already exists.")
            return redirect("list_category")

        category.name = name
        category.description = description
        category.status = status
        category.save()
        messages.success(request, f"Category '{name}' updated successfully.")
    return redirect("list_category")


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted successfully.")
    return redirect("list_category")

@login_required
def add_category(request):
    # Generate next category code for display
    last = Category.objects.order_by('-id').first()
    next_code = str((last.id + 1) if last else 1).zfill(4)

    if request.method == "POST":
        name                = request.POST.get("name", "").strip()
        display_on_branches = request.POST.get("display_on_branches", "").strip()
        days                = request.POST.get("days", "").strip()
        start_time          = request.POST.get("start_time") or None
        end_time            = request.POST.get("end_time") or None
        display_on_pos      = request.POST.get("display_on_pos") == "on"
        get_tax_from_item   = request.POST.get("get_tax_from_item") == "on"
        editable_sale_rate  = request.POST.get("editable_sale_rate") == "on"
        image               = request.FILES.get("image")

        if not name:
            messages.error(request, "Category name is required.")
            return redirect("add_category")

        if Category.objects.filter(name=name).exists():
            messages.error(request, "A category with this name already exists.")
            return redirect("add_category")

        Category.objects.create(
            name=name,
            display_on_branches=display_on_branches,
            days=days,
            start_time=start_time,
            end_time=end_time,
            display_on_pos=display_on_pos,
            get_tax_from_item=get_tax_from_item,
            editable_sale_rate=editable_sale_rate,
            image=image,
        )
        messages.success(request, f"Category '{name}' added successfully.")
        return redirect("list_category")

    return render(request, "categories/add_category.html", {
        "next_code": next_code
    })