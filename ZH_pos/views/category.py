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
def add_category(request):

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Category.objects.create(name=name)

        return redirect("list_category")

    return render(request, "categories/add_category.html")
