from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Category.objects.create(name=name)

        return redirect("list_category")

    return render(request, "categories/add_category.html")
