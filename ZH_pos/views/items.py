from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def list_items(request):
    return render(request, "items/list_items.html")

@login_required
def add_item(request):
    return render(request, "items/add_item.html")
