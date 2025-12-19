from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def sell(request):
    return render(request, "sales/sell.html")

@login_required
def sale_history(request):
    return render (request, "sales/sale_history.html")

@login_required 
def ecommerce_orders(request):
    return render(request, "sales/ecommerce_orders.html")

@login_required
def advance_booking(request):
    return render(request, "sales/advance_booking.html") 
