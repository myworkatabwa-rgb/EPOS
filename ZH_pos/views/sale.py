from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ZH_pos.models import Order

@login_required
def sell(request):
    return render(request, "sales/sell.html")

@login_required(login_url="/login/")
def sale_history(request):
    sales = (
        Order.objects
        .select_related("customer")
        .order_by("-created_at")
    )

    return render(
        request,
        "sales/sale_history.html",
        {"sales": sales}
    )

@login_required 
def ecommerce_orders(request):
    return render(request, "sales/ecommerce_orders.html")

@login_required
def advance_booking(request):
    return render(request, "sales/advance_booking.html") 
