from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ZH_pos.models import Category
from ZH_pos.woocommerce_webhook.py import sync_woo_categories


@login_required
def list_category(request):

    # 🔥 Call sync from woocommerce_api.py
    sync_woo_categories()

    categories = Category.objects.all()

    return render(request, "categories/list_category.html", {
        "categories": categories
    })
@login_required
def add_category(request):

    if request.method == "POST":
        name = request.POST.get("name")

        Category.objects.create(name=name)

        return redirect("list_category")

    return render(request, "categories/add_category.html")
