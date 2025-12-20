from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# EXISTING VIEW
@login_required
def vouchers(request):
    return render(request, "accounts/vouchers.html")


# NEW VIEWS START HERE

@login_required
def cash_payment_voucher(request):
    return render(request, "accounts/cash_payment_voucher.html")


@login_required
def cash_received_voucher(request):
    return render(request, "accounts/cash_received_voucher.html")


@login_required
def bank_payment_voucher(request):
    return render(request, "accounts/bank_payment_voucher.html")


@login_required
def bank_received_voucher(request):
    return render(request, "accounts/bank_received_voucher.html")


@login_required
def accounts_home(request):
    return render(request, "accounts/accounts.html")


@login_required
def chart_of_accounts(request):
    return render(request, "accounts/chart_of_accounts.html")


@login_required
def voucher_types(request):
    return render(request, "accounts/voucher_types.html")


@login_required
def credit_customers(request):
    return render(request, "accounts/credit_customers.html")
