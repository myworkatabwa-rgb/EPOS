from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inventory(request):
    return render(request, "inventory/inventory.html")


@login_required
def physical_stock(request):
    return render(request, "inventory/physical_stock.html")


@login_required
def stock_audit_form(request):
    return render(request, "inventory/stock_audit_form.html")


@login_required
def item_conversion(request):
    return render(request, "inventory/item_conversion.html")


@login_required
def demand_sheet(request):
    return render(request, "inventory/demand_sheet.html")


@login_required
def purchase_order(request):
    return render(request, "inventory/purchase_order.html")


@login_required
def goods_receive_note(request):
    return render(request, "inventory/goods_receive_note.html")


@login_required
def goods_receive_return_note(request):
    return render(request, "inventory/goods_receive_return_note.html")


@login_required
def item_recipe(request):
    return render(request, "inventory/item_recipe.html")


@login_required
def transfer_out(request):
    return render(request, "inventory/transfer_out.html")


@login_required
def transfer_in(request):
    return render(request, "inventory/transfer_in.html")
