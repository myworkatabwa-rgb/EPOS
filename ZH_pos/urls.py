from django.urls import path
from ZH_pos import views

# SALES
from .views.sale import (
    sell,
    sale_history,
    ecommerce_orders,
    advance_booking,
    sale_receipt,
    delete_sale,
    packing_slip,
    packing_history,
)

# Returns

# TRANSACTIONS
from .views.returns import (
    sale_returns,
    sale_return_history,
    fetch_sale_for_return,
    confirm_sale_return,
)

# ITEMS (IMPORT ALL ITEM VIEWS HERE)
from .views.items import import_items
from .views.items import (
    list_items,
    add_item,
    delete_items,
    item_modifiers,
    search_products,
    save_modifiers,
    modifiers_list,
    suppliers,
    supplier_list,
    add_brand,
    brand_list,
    delete_brand,
    edit_brand,
    search_items,
    print_multiple_barcodes,
    barcode_search_api,
    generate_barcodes,
    barcode_preview,
    discount,
    discount_list,
    colors,
    Color_list,
    delete_Color,
    edit_Color,
    sizes,
    Size_list,
    delete_Size,
    edit_Size,
    units,
    Unit_list,
    delete_Unit,
    edit_Unit,
    promotions,
    promotion_list,
    promotion_add,
    promotion_delete,
    promotion_edit,
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
    #path("returns/<str:order_id>/", views.process_return, name="process_return"),
    #path ("returns/", sale_returns),
    path("returns/", sale_returns),
    path("returns/fetch-sale/", fetch_sale_for_return, name="fetch_sale_for_return"),
    path("returns/confirm/", confirm_sale_return, name="confirm_sale_return"),
    path("returns/history/", sale_return_history),

    # SALES
    path("sales/", sell),
    path("sales/history/", sale_history),
    path("sales/receipt/<str:order_id>/", sale_receipt),   
    path('sales/delete/<str:order_id>/', delete_sale, name='delete_sale'),
    path("sales/ecommerce/", ecommerce_orders),
    path("sales/advance/", advance_booking),
    path ("sales/packing_sl/", packing_slip),
    path("sales/packing_his/", packing_history),

    # TRANSACTIONS
   # path("returns/", sale_returns),
    #path("returns/history/", sale_return_history),

    # ITEMS ✅ (NOW CORRECT)
    path("items/", list_items, name="list_items"),
    path("items/import/", import_items, name="import_items"),
    path('items/delete/', delete_items, name='delete_items'),
    path("items/add/", add_item, name="add_item"),
    path("items/modifiers/", item_modifiers, name="item_modifiers"),
    path("items/modifiers/search/", search_products, name="search_products"),
    path("items/modifiers/save/", save_modifiers, name="save_modifiers"),
    path("items/modifiers/list/", modifiers_list, name="modifiers_list"),
    path("items/suppliers/", suppliers, name="suppliers"),
    path("items/supplier-list/", supplier_list, name="supplier_list"),
    path("items/brands/add/", add_brand, name="add_brand"),
    path("items/brands/", brand_list, name="brand_list"),
    path("items/brands/delete/<int:id>/", delete_brand, name="delete_brand"),
    path("items/brands/<int:id>/edit/", edit_brand, name="edit_brand"),
    path("items/search/", search_items, name="search_items"),
    path("items/print-barcodes/", print_multiple_barcodes, name="print_multiple_barcodes"),
    path("api/barcode-search/", barcode_search_api, name="barcode_search_api"),
    path("items/generate-barcodes/", generate_barcodes, name="generate_barcodes"),
    path("items/barcode_preview/" , barcode_preview, name="barcode_preview"),
    path("items/discount/", discount, name="discount"),
    path("items/list/", discount_list, name="discount_list"),
    path("items/colors/", colors, name="colors"),
    path("items/colors/list/", Color_list, name="Color_list"),
    path("items/colors/delete/<int:id>/", delete_Color, name="delete_Color"),
    path("items/colors/edit/<int:id>/", edit_Color, name="edit_Color"),
    path("items/sizes/", sizes, name="sizes"),
    path("items/sizes/list/", Size_list, name="Size_list"),
    path("items/sizes/delete/<int:id>/", delete_Size, name="delete_Size"),
    path("items/sizes/edit/<int:id>/", edit_Size, name="edit_Size"),
    path("items/units/", units, name="units"),
    path("items/units/list/", Unit_list, name="Unit_list"),
    path("items/units/delete/<int:id>/", delete_Unit, name="delete_Unit"),
    path("items/units/edit/<int:id>/", edit_Unit, name="edit_Unit"),
    path("items/promotions/", promotions, name="promotions"),
    path("items/promotions/add/", promotion_add, name="promotion_add"),
    path("items/promotions/delete/<int:id>/", promotion_delete, name="promotion_delete"),
    path("items/promotions/edit/<int:id>/", promotion_edit, name="promotion_edit"),
    path("items/price-list/", views.items.price_list, name='price_list'),
    path("items/ajax/get-item/", views.items.get_item_by_barcode, name='get_item_by_barcode'),
    path("items/price-list/save/", views.items.save_price_list, name='save_price_list'),
    path("items/search-products/", views.items.search_products, name="search_products"),
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
