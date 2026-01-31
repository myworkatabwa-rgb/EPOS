from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def sale_returns(request):
    return render(request, "returns/sale_returns.html")

@login_required 
def sale_return_history(request):
    return render (request, "returns/sale_return_history.html")
