from django.urls import path
from ZH_pos import views
from .views.sale import sell, sale_history, ecommerce_orders
from .views.transaction import sale_returns, sale_return_history
from .views.items import list_items, add_item
from .views.inventory import inventory
from .views.accounts import vouchers
from .views.settings import settings_home, users
from .views.financial_dashboard import financial_dashboard

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("finance/financial_dashboard/", financial_dashboard, name="financial_dashboard"),
    path("pos/", views.pos_view, name="pos"),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),
    path("returns/<str:order_id>/", views.process_return, name="process_return"),
    
    # SALES
    path("sales/", sell),
    path("sales/history/", sale_history),
    path("sales/ecommerce/", ecommerce_orders),
    path("sales/advanced/", advanced_booking),

    # TRANSACTIONS
    path("returns/", sale_returns),
    path("returns/history/", sale_return_history),

    # ITEMS
    path("items/", list_items),
    path("items/add/", add_item),

    # INVENTORY
    path("inventory/", inventory),

    # ACCOUNTS
    path("accounts/vouchers/", vouchers),

    # SETTINGS
    path("settings/", settings_home),
    path("settings/users/", users),
]
