from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# EXISTING VIEWS
@login_required
def settings_home(request):
    return render(request, "settings/settings.html")

@login_required
def users(request):
    return render(request, "settings/users.html")


# NEW VIEWS
@login_required
def roles(request):
    return render(request, "settings/roles.html")

@login_required
def branches(request):
    return render(request, "settings/branches.html")

@login_required
def cisepos_payment_invoices(request):
    return render(request, "settings/cisepos_payment_invoices.html")

@login_required
def channels(request):
    return render(request, "settings/channels.html")

@login_required
def banks(request):
    return render(request, "settings/banks.html")

@login_required
def counters(request):
    return render(request, "settings/counters.html")

@login_required
def shifts(request):
    return render(request, "settings/shifts.html")

@login_required
def taxes(request):
    return render(request, "settings/taxes.html")

@login_required
def ip_restrictions(request):
    return render(request, "settings/ip_restrictions.html")

@login_required
def billing(request):
    return render(request, "settings/billing.html")

@login_required
def sms_setup(request):
    return render(request, "settings/sms_setup.html")

@login_required
def ecommerce_setup(request):
    return render(request, "settings/ecommerce_setup.html")
