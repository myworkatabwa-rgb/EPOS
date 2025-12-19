from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Q

from ..models import Order, Customer


@login_required
def financial_dashboard(request):
    # =========================
    # INCOME & EXPENSE
    # =========================
    total_income = Order.objects.filter(status="completed").aggregate(total=Sum("total"))["total"] or 0
    total_expense = 0  # Placeholder for expense vouchers later

    # =========================
    # ACCOUNTS RECEIVABLE (from pending orders)
    # =========================
    accounts_receivable = (
        Order.objects
        .filter(status="pending")
        .aggregate(total=Sum("total"))["total"] or 0
    )

    accounts_payable = 0  # Placeholder for supplier payments

    # =========================
    # PURCHASE
    # =========================
    total_purchase = 0  # Placeholder for purchase orders

    # =========================
    # CASH & BANK
    # =========================
    cash_sale = Order.objects.filter(payment_method="cash", status="completed").aggregate(total=Sum("total"))["total"] or 0
    bank_sale = Order.objects.filter(payment_method__in=["card", "bank"], status="completed").aggregate(total=Sum("total"))["total"] or 0
    cash_bank_balance = cash_sale + bank_sale

    # =========================
    # ACCOUNT SUMMARY
    # =========================
    assets = [
        {"name": "Cash In Hand", "amount": cash_sale},
        {"name": "Bank", "amount": bank_sale},
        {"name": "Accounts Receivable", "amount": accounts_receivable},
    ]

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "accounts_receivable": accounts_receivable,
        "accounts_payable": accounts_payable,
        "total_purchase": total_purchase,
        "cash_bank_balance": cash_bank_balance,
        "assets": assets,
    }

    return render(request, "finance/financial_dashboard.html", context)
