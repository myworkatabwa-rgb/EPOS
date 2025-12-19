from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def settings_home(request):
    return render(request, "settings/settings.html")

@login_required
def users(request):
    return render(request, "settings/users.html")
