from django.urls import path
from ZH_pos import views
from .views.sale import sell, sale_history, ecommerce_orders, advance_booking
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
    path("sales/advance/", advance_booking),

    # TRANSACTIONS
    path("returns/", sale_returns),
    path("returns/history/", sale_return_history),

    # ITEMS
    path("items/", list_items),
    path("items/add/", add_item),
    path("items/modifiers/", views.item_modifiers, name='item_modifiers'),
    path("items/suppliers/", views.suppliers, name='suppliers'),
    path("items/brands/", views.brands, name='brands'),
    path("items/search/", views.search_item, name='search_item'),
    path("items/print-barcodes/", views.print_multiple_barcodes, name='print_multiple_barcodes'),
    path("items/discount/", views.discount, name='discount'),
    path("items/colors/", views.colors, name='colors'),
    path("items/sizes/", views.sizes, name='sizes'),
    path("items/units/", views.units, name='units'),
    path("items/promotions/", views.promotions, name='promotions'),
    path("items/price-list/", views.price_list, name='price_list'),
    path("items/bulk-update/", views.bulk_update, name='bulk_update'),
    path("items/price-checker/", views.price_checker, name='price_checker'),
    path("items/courier/", views.courier, name='courier'),
    path("items/sales-target/", views.sales_target, name='sales_target'),


    # INVENTORY
    path("inventory/", inventory),

    # ACCOUNTS
    path("accounts/vouchers/", vouchers),

    # SETTINGS
    path("settings/", settings_home),
    path("settings/users/", users),
]
