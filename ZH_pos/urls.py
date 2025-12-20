from django.urls import path
from ZH_pos import views

# SALES
from .views.sale import sell, sale_history, ecommerce_orders, advance_booking, , sale_receipt

# TRANSACTIONS
from .views.transaction import sale_returns, sale_return_history

# ITEMS (IMPORT ALL ITEM VIEWS HERE)
from .views.items import (
    list_items,
    add_item,
    item_modifiers,
    suppliers,
    brands,
    search_item,
    print_multiple_barcodes,
    discount,
    colors,
    sizes,
    units,
    promotions,
    price_list,
    bulk_update,
    price_checker,
    courier,
    sales_target,
)

# INVENTORY
from .views.inventory import (
    inventory,
    physical_stock,
    stock_audit_form,
    item_conversion,
    demand_sheet,
    purchase_order,
    goods_receive_note,
    goods_receive_return_note,
    item_recipe,
    transfer_out,
    transfer_in,
)
# ACCOUNTS
from .views.accounts import (
    vouchers,
    cash_payment_voucher,
    cash_received_voucher,
    bank_payment_voucher,
    bank_received_voucher,
    accounts_home,
    chart_of_accounts,
    voucher_types,
    credit_customers,
)
# SETTINGS
from .views.settings import (
    settings_home,
    users,
    roles,
    branches,
    cisepos_payment_invoices,
    channels,
    banks,
    counters,
    shifts,
    taxes,
    ip_restrictions,
    billing,
    sms_setup,
    ecommerce_setup,
)

# FINANCE
from .views.financial_dashboard import financial_dashboard


urlpatterns = [
    # DASHBOARD
    path("", views.dashboard, name="dashboard"),
    path("finance/financial_dashboard/", financial_dashboard, name="financial_dashboard"),

    # POS
    path("pos/", views.pos_view, name="pos"),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),

    # RETURNS
    path("returns/<str:order_id>/", views.process_return, name="process_return"),

    # SALES
    path("sales/", sell),
    path("sales/history/", sale_history),
    path("sales/receipt/<str:order_id>/", sale_receipt),
    path("sales/ecommerce/", ecommerce_orders),
    path("sales/advance/", advance_booking),

    # TRANSACTIONS
    path("returns/", sale_returns),
    path("returns/history/", sale_return_history),

    # ITEMS ✅ (NOW CORRECT)
    path("items/", list_items, name="list_items"),
    path("items/add/", add_item, name="add_item"),
    path("items/modifiers/", item_modifiers, name="item_modifiers"),
    path("items/suppliers/", suppliers, name="suppliers"),
    path("items/brands/", brands, name="brands"),
    path("items/search/", search_item, name="search_item"),
    path("items/print-barcodes/", print_multiple_barcodes, name="print_multiple_barcodes"),
    path("items/discount/", discount, name="discount"),
    path("items/colors/", colors, name="colors"),
    path("items/sizes/", sizes, name="sizes"),
    path("items/units/", units, name="units"),
    path("items/promotions/", promotions, name="promotions"),
    path("items/price-list/", price_list, name="price_list"),
    path("items/bulk-update/", bulk_update, name="bulk_update"),
    path("items/price-checker/", price_checker, name="price_checker"),
    path("items/courier/", courier, name="courier"),
    path("items/sales-target/", sales_target, name="sales_target"),

    
   # INVENTORY
    path("inventory/", inventory, name="inventory"),
    path("inventory/physical-stock/", physical_stock, name="physical_stock"),
    path("inventory/stock-audit-form/", stock_audit_form, name="stock_audit_form"),
    path("inventory/item-conversion/", item_conversion, name="item_conversion"),
    path("inventory/demand-sheet/", demand_sheet, name="demand_sheet"),
    path("inventory/purchase-order/", purchase_order, name="purchase_order"),
    path("inventory/goods-receive-note/", goods_receive_note, name="goods_receive_note"),
    path("inventory/goods-receive-return-note/", goods_receive_return_note, name="goods_receive_return_note"),
    path("inventory/item-recipe/", item_recipe, name="item_recipe"),
    path("inventory/transfer-out/", transfer_out, name="transfer_out"),
    path("inventory/transfer-in/", transfer_in, name="transfer_in"),

    # ACCOUNTS
    path("accounts/vouchers/", vouchers, name="vouchers"),
    path("accounts/cash-payment-voucher/", cash_payment_voucher, name="cash_payment_voucher"),
    path("accounts/cash-received-voucher/", cash_received_voucher, name="cash_received_voucher"),
    path("accounts/bank-payment-voucher/", bank_payment_voucher, name="bank_payment_voucher"),
    path("accounts/bank-received-voucher/", bank_received_voucher, name="bank_received_voucher"),
    path("accounts/", accounts_home, name="accounts_home"),
    path("accounts/chart-of-accounts/", chart_of_accounts, name="chart_of_accounts"),
    path("accounts/voucher-types/", voucher_types, name="voucher_types"),
    path("accounts/credit-customers/", credit_customers, name="credit_customers"),

    path("settings/", settings_home, name="settings_home"),
    path("settings/users/", users, name="users"),
    path("settings/roles/", roles, name="roles"),
    path("settings/branches/", branches, name="branches"),
    path("settings/cisepos-payment-invoices/", cisepos_payment_invoices, name="cisepos_payment_invoices"),
    path("settings/channels/", channels, name="channels"),
    path("settings/banks/", banks, name="banks"),
    path("settings/counters/", counters, name="counters"),
    path("settings/shifts/", shifts, name="shifts"),
    path("settings/taxes/", taxes, name="taxes"),
    path("settings/ip-restrictions/", ip_restrictions, name="ip_restrictions"),
    path("settings/billing/", billing, name="billing"),
    path("settings/sms-setup/", sms_setup, name="sms_setup"),
    path("settings/ecommerce-setup/", ecommerce_setup, name="ecommerce_setup"),

]
