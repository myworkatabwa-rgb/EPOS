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
    path('modifiers/', views.item_modifiers, name='item_modifiers'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('brands/', views.brands, name='brands'),
    path('search/', views.search_item, name='search_item'),
    path('print-barcodes/', views.print_multiple_barcodes, name='print_multiple_barcodes'),
    path('discount/', views.discount, name='discount'),
    path('colors/', views.colors, name='colors'),
    path('sizes/', views.sizes, name='sizes'),
    path('units/', views.units, name='units'),
    path('promotions/', views.promotions, name='promotions'),
    path('price-list/', views.price_list, name='price_list'),
    path('bulk-update/', views.bulk_update, name='bulk_update'),
    path('price-checker/', views.price_checker, name='price_checker'),
    path('courier/', views.courier, name='courier'),
    path('sales-target/', views.sales_target, name='sales_target'),


    # INVENTORY
    path("inventory/", inventory),

    # ACCOUNTS
    path("accounts/vouchers/", vouchers),

    # SETTINGS
    path("settings/", settings_home),
    path("settings/users/", users),
]
