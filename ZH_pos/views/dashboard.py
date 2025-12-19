from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required

from ZH_pos.models import Order, OrderItem


@login_required(login_url="/login/")
def dashboard(request):
    today = now().date()
    yesterday = today - timedelta(days=1)

    # ---- TODAY ----
    today_orders = Order.objects.filter(created_at__date=today)
    today_total = today_orders.aggregate(total=Sum("total"))["total"] or 0
    today_count = today_orders.count()

    cash_sale = today_orders.filter(
        payment_method="cash"
    ).aggregate(total=Sum("total"))["total"] or 0

    card_sale = today_orders.filter(
        payment_method="card"
    ).aggregate(total=Sum("total"))["total"] or 0

    split_sale = today_orders.filter(
        payment_method="split"
    ).aggregate(total=Sum("total"))["total"] or 0

    # ---- YESTERDAY ----
    yesterday_total = (
        Order.objects
        .filter(created_at__date=yesterday)
        .aggregate(total=Sum("total"))["total"] or 0
    )

    # ---- ITEM WISE (30 DAYS) ----
    last_30 = now() - timedelta(days=30)
    item_sales = (
        OrderItem.objects
        .filter(order__created_at__gte=last_30)
        .values("product__name")
        .annotate(
            quantity=Sum("quantity"),
            amount=Sum("total")
        )
    )

    # ---- SALES CHART ----
    sales_chart = list(
        Order.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )

    context = {
        "today_total": today_total,
        "today_count": today_count,
        "cash_sale": cash_sale,
        "card_sale": card_sale,
        "split_sale": split_sale,
        "yesterday_total": yesterday_total,
        "item_sales": item_sales,
        "sales_chart": sales_chart,
    }

    return render(request, "dashboard.html", context)

