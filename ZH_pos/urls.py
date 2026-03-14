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

# CATEGORIES
from .views.category import (
    list_category,
    add_category,
    edit_category,
    delete_category,
)

# RETURNS
from .views.returns import (
    sale_returns,
    sale_return_history,
    fetch_sale_for_return,
    confirm_sale_return,
)

# ITEMS
from .views.items import import_items
from .views.items import (
    list_items,
    add_item,
    get_subcategories,
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
    sales_target,
)

# INVENTORY
from .views.inventory import (
    inventory,
    physical_stock_list,
    physical_stock_create,
    physical_stock_delete,
    load_products_by_category,
    load_subcategories,
    physical_stock_detail,
    stock_audit_list,
    stock_audit_create,
    stock_audit_detail,
    stock_audit_delete,
    fetch_product_by_barcode,
    item_conversion_list,
    item_conversion_create,
    item_conversion_detail,
    item_conversion_delete,
    search_product_for_conversion,
    demand_sheet_list,
    demand_sheet_create,
    demand_sheet_detail,
    demand_sheet_delete,
    load_consumption,
    purchase_order_list,
    purchase_order_create,
    purchase_order_detail,
    purchase_order_receive,
    purchase_order_delete,
    load_demand_sheet_items,
    search_product_for_po,
    grn_list,
    grn_create,
    grn_detail,
    grn_delete,
    load_po_items,
    fetch_product_for_grn,
    goods_receive_return_note,
    grn_return_list,
    grn_return_detail,
    grn_return_delete,
    load_grn_items,
    item_recipe_list,
    item_recipe_create,
    item_recipe_edit,
    item_recipe_detail,
    item_recipe_delete,
    search_raw_material,
    get_recipe_for_product,
    transfer_out_list,
    transfer_out_create,
    transfer_out_detail,
    transfer_out_delete,
    load_demand_for_transfer,
    load_grn_for_transfer,
    transfer_in,
    transfer_in_list,
    transfer_in_create,
    transfer_in_detail,
    transfer_in_delete,
    load_transfer_out_items,
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

    # ── DASHBOARD ────────────────────────────────────────────
    path("", views.dashboard, name="dashboard"),
    path("finance/financial_dashboard/", financial_dashboard, name="financial_dashboard"),

    # ── POS ──────────────────────────────────────────────────
    path("pos/",          views.pos_view,    name="pos"),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),

    # ── RETURNS ──────────────────────────────────────────────
    path("returns/",                          sale_returns,             name="sale_returns"),
    path("returns/fetch-sale/",               fetch_sale_for_return,    name="fetch_sale_for_return"),
    path("returns/confirm/",                  confirm_sale_return,      name="confirm_sale_return"),
    path("returns/history/",                  sale_return_history,      name="sale_return_history"),
    path("returns/delete/<int:return_id>/",   views.delete_return,      name="delete_return"),
    path("returns/detail/<int:return_id>/",   views.return_detail,      name="return_detail"),

    # ── CATEGORIES ───────────────────────────────────────────
    path("categories/",                          list_category,   name="list_category"),
    path("categories/add/",                      add_category,    name="add_category"),
    path("categories/edit/<int:category_id>/",   edit_category,   name="edit_category"),
    path("categories/delete/<int:category_id>/", delete_category, name="delete_category"),

    # ── SALES ────────────────────────────────────────────────
    path("sales/",                              sell,          name="sell"),
    path("sales/history/",                      sale_history,  name="sale_history"),
    path("sales/receipt/<str:order_id>/",       sale_receipt,  name="sale_receipt"),
    path("sales/delete/<str:order_id>/",        delete_sale,   name="delete_sale"),
    path("sales/ecommerce/",                    ecommerce_orders, name="ecommerce_orders"),
    path("sales/advance/",                      advance_booking,  name="advance_booking"),
    path("sales/packing_sl/",                   packing_slip,     name="packing_slip"),
    path("sales/packing_his/",                  packing_history,  name="packing_his"),
    path("bookings/detail/<str:booking_no>/",   views.sale.booking_detail,  name="booking_detail"),
    path("sales/packing/delete/<str:booking_no>/", views.sale.delete_booking, name="delete_booking"),

    # ── ITEMS ────────────────────────────────────────────────
    path("items/",                              list_items,              name="list_items"),
    path("items/import/",                       import_items,            name="import_items"),
    path("items/delete/",                       delete_items,            name="delete_items"),
    path("items/add/",                          add_item,                name="add_item"),
    path("items/subcategories/",                get_subcategories,       name="get_subcategories"),
    path("items/modifiers/",                    item_modifiers,          name="item_modifiers"),
    path("items/modifiers/search/",             search_products,         name="search_products"),
    path("items/modifiers/save/",               save_modifiers,          name="save_modifiers"),
    path("items/modifiers/list/",               modifiers_list,          name="modifiers_list"),
    path("items/suppliers/",                    suppliers,               name="suppliers"),
    path("items/supplier-list/",                supplier_list,           name="supplier_list"),
    path("items/brands/add/",                   add_brand,               name="add_brand"),
    path("items/brands/",                       brand_list,              name="brand_list"),
    path("items/brands/delete/<int:id>/",       delete_brand,            name="delete_brand"),
    path("items/brands/<int:id>/edit/",         edit_brand,              name="edit_brand"),
    path("items/search/",                       search_items,            name="search_items"),
    path("items/print-barcodes/",               print_multiple_barcodes, name="print_multiple_barcodes"),
    path("api/barcode-search/",                 barcode_search_api,      name="barcode_search_api"),
    path("items/generate-barcodes/",            generate_barcodes,       name="generate_barcodes"),
    path("items/barcode_preview/",              barcode_preview,         name="barcode_preview"),
    path("items/discount/",                     discount,                name="discount"),
    path("items/list/",                         discount_list,           name="discount_list"),
    path("items/colors/",                       colors,                  name="colors"),
    path("items/colors/list/",                  Color_list,              name="Color_list"),
    path("items/colors/delete/<int:id>/",       delete_Color,            name="delete_Color"),
    path("items/colors/edit/<int:id>/",         edit_Color,              name="edit_Color"),
    path("items/sizes/",                        sizes,                   name="sizes"),
    path("items/sizes/list/",                   Size_list,               name="Size_list"),
    path("items/sizes/delete/<int:id>/",        delete_Size,             name="delete_Size"),
    path("items/sizes/edit/<int:id>/",          edit_Size,               name="edit_Size"),
    path("items/units/",                        units,                   name="units"),
    path("items/units/list/",                   Unit_list,               name="Unit_list"),
    path("items/units/delete/<int:id>/",        delete_Unit,             name="delete_Unit"),
    path("items/units/edit/<int:id>/",          edit_Unit,               name="edit_Unit"),
    path("items/promotions/",                   promotions,              name="promotions"),
    path("items/promotions/add/",               promotion_add,           name="promotion_add"),
    path("items/promotions/delete/<int:id>/",   promotion_delete,        name="promotion_delete"),
    path("items/promotions/edit/<int:id>/",     promotion_edit,          name="promotion_edit"),
    path("items/promotions/list/",              promotion_list,          name="promotion_list"),
    path("items/price-list/",                   views.items.price_list,          name="price_list"),
    path("items/ajax/get-item/",                views.items.get_item_by_barcode, name="get_item_by_barcode"),
    path("items/price-list/save/",              views.items.save_price_list,     name="save_price_list"),
    path("items/price-lists/",                  views.items.list_price_lists,    name="list_price_lists"),
    path("items/price-lists/<int:pk>/",         views.items.price_list_detail,   name="price_list_detail"),
    path("items/search-products/",              views.items.search_products,     name="search_products"),
    path("items/bulk-update/",                  views.items.bulk_update,         name="bulk_update"),
    path("items/bulk-update/load-items/",       views.items.load_bulk_items,     name="load_bulk_items"),
    path("items/bulk-update/save/",             views.items.save_bulk_update,    name="save_bulk_update"),
    path("items/price-checker/",                price_checker,                   name="price_checker"),
    path("items/ajax/price-checker-search/",    views.items.price_checker_search, name="price_checker_search"),
    path("items/courier/",                      views.items.courier_list,        name="courier_list"),
    path("items/courier/add/",                  views.items.courier_add,         name="courier_add"),
    path("items/courier/edit/<int:id>/",        views.items.courier_edit,        name="courier_edit"),
    path("items/courier/delete/<int:id>/",      views.items.courier_delete,      name="courier_delete"),
    path("items/sales-target/",                 sales_target,                    name="sales_target"),

    # ── INVENTORY ────────────────────────────────────────────
    path("inventory/",                                      inventory,                  name="inventory"),

    # Physical Stock
    path("inventory/physical-stock/",                       physical_stock_list,        name="physical_stock_list"),
    path("inventory/physical-stock/create/",                physical_stock_create,      name="physical_stock_create"),
    path("inventory/physical-stock/<int:pk>/",              physical_stock_detail,      name="physical_stock_detail"),
    path("inventory/physical-stock/delete/<int:stock_id>/", physical_stock_delete,      name="physical_stock_delete"),
    path("inventory/load-products/",                        load_products_by_category,  name="load_products_by_category"),
    path("inventory/load-subcategories/",                   load_subcategories,         name="load_subcategories"),

    # Stock Audit
    path("inventory/stock-audit/",                  stock_audit_list,         name="stock_audit_list"),
    path("inventory/stock-audit/create/",           stock_audit_create,       name="stock_audit_create"),
    path("inventory/stock-audit/<int:pk>/",         stock_audit_detail,       name="stock_audit_detail"),
    path("inventory/stock-audit/delete/<int:pk>/",  stock_audit_delete,       name="stock_audit_delete"),
    path("inventory/fetch-product-barcode/",        fetch_product_by_barcode, name="fetch_product_by_barcode"),

    # Item Conversion
    path("inventory/item-conversion/",                  item_conversion_list,          name="item_conversion_list"),
    path("inventory/item-conversion/create/",           item_conversion_create,        name="item_conversion_create"),
    path("inventory/item-conversion/<int:pk>/",         item_conversion_detail,        name="item_conversion_detail"),
    path("inventory/item-conversion/delete/<int:pk>/",  item_conversion_delete,        name="item_conversion_delete"),
    path("inventory/search-product-conversion/",        search_product_for_conversion, name="search_product_for_conversion"),

    # Demand Sheet
    path("inventory/demand-sheet/",                 demand_sheet_list,   name="demand_sheet_list"),
    path("inventory/demand-sheet/create/",          demand_sheet_create, name="demand_sheet_create"),
    path("inventory/demand-sheet/<int:pk>/",        demand_sheet_detail, name="demand_sheet_detail"),
    path("inventory/demand-sheet/delete/<int:pk>/", demand_sheet_delete, name="demand_sheet_delete"),
    path("inventory/load-consumption/",             load_consumption,    name="load_consumption"),

    # Purchase Order
    path("inventory/purchase-order/",                    purchase_order_list,     name="purchase_order_list"),
    path("inventory/purchase/create/",                   purchase_order_create,   name="purchase_order_create"),
    path("inventory/purchase/<int:pk>/",                 purchase_order_detail,   name="purchase_order_detail"),
    path("inventory/purchase/<int:pk>/receive/",         purchase_order_receive,  name="purchase_order_receive"),
    path("inventory/purchase/delete/<int:pk>/",          purchase_order_delete,   name="purchase_order_delete"),
    path("inventory/purchase/load-demand-items/",        load_demand_sheet_items, name="load_demand_sheet_items"),
    path("inventory/purchase/search-product/",           search_product_for_po,   name="search_product_for_po"),

    # GRN
    path("inventory/grn/",                  grn_list,              name="grn_list"),
    path("inventory/grn/create/",           grn_create,            name="grn_create"),
    path("inventory/grn/<int:pk>/",         grn_detail,            name="grn_detail"),
    path("inventory/grn/delete/<int:pk>/",  grn_delete,            name="grn_delete"),
    path("inventory/grn/load-po-items/",    load_po_items,         name="load_po_items"),
    path("inventory/grn/fetch-product/",    fetch_product_for_grn, name="fetch_product_for_grn"),

    # GRN Return
    path("inventory/grn-return/",                 grn_return_list,           name="grn_return_list"),
    path("inventory/grn-return/create/",          goods_receive_return_note, name="goods_receive_return_note"),
    path("inventory/grn-return/<int:pk>/",        grn_return_detail,         name="grn_return_detail"),
    path("inventory/grn-return/delete/<int:pk>/", grn_return_delete,         name="grn_return_delete"),
    path("inventory/grn-return/load-grn-items/",  load_grn_items,            name="load_grn_items"),

    # Item Recipe
    path("inventory/item-recipe/",                  item_recipe_list,       name="item_recipe_list"),
    path("inventory/item-recipe/create/",           item_recipe_create,     name="item_recipe_create"),
    path("inventory/item-recipe/search-material/",  search_raw_material,    name="search_raw_material"),
    path("inventory/item-recipe/get-recipe/",       get_recipe_for_product, name="get_recipe_for_product"),
    path("inventory/item-recipe/<int:pk>/",         item_recipe_detail,     name="item_recipe_detail"),
    path("inventory/item-recipe/edit/<int:pk>/",    item_recipe_edit,       name="item_recipe_edit"),
    path("inventory/item-recipe/delete/<int:pk>/",  item_recipe_delete,     name="item_recipe_delete"),

    # Transfer Out
    path("inventory/transfer-out/",                  transfer_out_list,        name="transfer_out_list"),
    path("inventory/transfer-out/create/",           transfer_out_create,      name="transfer_out_create"),
    path("inventory/transfer-out/load-demand/",      load_demand_for_transfer, name="load_demand_for_transfer"),
    path("inventory/transfer-out/load-grn/",         load_grn_for_transfer,    name="load_grn_for_transfer"),
    path("inventory/transfer-out/<int:pk>/",         transfer_out_detail,      name="transfer_out_detail"),
    path("inventory/transfer-out/delete/<int:pk>/",  transfer_out_delete,      name="transfer_out_delete"),

    # Transfer In
    path("inventory/transfer-in/", transfer_in, name="transfer_in"),

    # ── ACCOUNTS ─────────────────────────────────────────────
    path("accounts/",                       accounts_home,            name="accounts_home"),
    path("accounts/vouchers/",              vouchers,                 name="vouchers"),
    path("accounts/cash-payment-voucher/",  cash_payment_voucher,     name="cash_payment_voucher"),
    path("accounts/cash-received-voucher/", cash_received_voucher,    name="cash_received_voucher"),
    path("accounts/bank-payment-voucher/",  bank_payment_voucher,     name="bank_payment_voucher"),
    path("accounts/bank-received-voucher/", bank_received_voucher,    name="bank_received_voucher"),
    path("accounts/chart-of-accounts/",     chart_of_accounts,        name="chart_of_accounts"),
    path("accounts/voucher-types/",         voucher_types,            name="voucher_types"),
    path("accounts/credit-customers/",      credit_customers,         name="credit_customers"),

    # ── SETTINGS ─────────────────────────────────────────────
    path("settings/",                           settings_home,               name="settings_home"),
    path("settings/users/",                     users,                       name="users"),
    path("settings/roles/",                     roles,                       name="roles"),
    path("settings/branches/",                  branches,                    name="branches"),
    path("settings/cisepos-payment-invoices/",  cisepos_payment_invoices,    name="cisepos_payment_invoices"),
    path("settings/channels/",                  channels,                    name="channels"),
    path("settings/banks/",                     banks,                       name="banks"),
    path("settings/counters/",                  counters,                    name="counters"),
    path("settings/shifts/",                    shifts,                      name="shifts"),
    path("settings/taxes/",                     taxes,                       name="taxes"),
    path("settings/ip-restrictions/",           ip_restrictions,             name="ip_restrictions"),
    path("settings/billing/",                   billing,                     name="billing"),
    path("settings/sms-setup/",                 sms_setup,                   name="sms_setup"),
    path("settings/ecommerce-setup/",           ecommerce_setup,             name="ecommerce_setup"),
]