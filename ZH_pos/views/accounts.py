from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ZH_pos.models import Voucher, VoucherItem, VoucherType, Branch, Account, AccountGroup, AccountLedgerEntry


# EXISTING VIEW
@login_required
def vouchers(request):
    return render(request, "accounts/vouchers.html")
def generate_voucher_no(voucher_type_code="VCH"):
    last = Voucher.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    today = timezone.now().strftime("%d%m%Y")
    return f"{today}{str(next_id).zfill(4)}"


@login_required
def voucher_list(request):
    vouchers = Voucher.objects.select_related(
        "branch", "voucher_type", "created_by"
    ).order_by("-created_at")
    return render(request, "accounts/voucher_list.html", {
        "vouchers": vouchers
    })


@login_required
def voucher_create(request):
    voucher_types = VoucherType.objects.all().order_by("code")
    branches      = Branch.objects.all().order_by("name")
    main_branch   = Branch.objects.filter(is_main=True).first()
    today         = timezone.now().strftime("%-d-%-m-%Y")

    if request.method == "POST":
        try:
            data            = json.loads(request.body)
            voucher_type_id = data.get("voucher_type_id") or None
            narration       = data.get("narration", "")
            bill_ref_no     = data.get("bill_ref_no", "")
            items           = data.get("items", [])

            if not voucher_type_id:
                return JsonResponse({"success": False, "error": "Please select voucher type."})

            if not items:
                return JsonResponse({"success": False, "error": "Please add at least one entry."})

            # Get voucher type code for number generation
            vtype        = VoucherType.objects.get(id=voucher_type_id)
            voucher_no   = generate_voucher_no(vtype.code)
            total_amount = sum(float(i.get("amount", 0)) for i in items)

            voucher = Voucher.objects.create(
                voucher_no      = voucher_no,
                branch          = main_branch,
                voucher_type_id = voucher_type_id,
                narration       = narration,
                bill_ref_no     = bill_ref_no,
                total_amount    = total_amount,
                created_by      = request.user,
            )

            for item in items:
                account_name = item.get("account_name", "")
                description  = item.get("description", "")
                debit_credit = item.get("debit_credit", "debit")
                amount       = float(item.get("amount", 0))

                if not account_name or amount <= 0:
                    continue

                VoucherItem.objects.create(
                    voucher_id   = voucher.id,
                    account_name = account_name,
                    description  = description,
                    debit_credit = debit_credit,
                    amount       = amount,
                )

            return JsonResponse({"success": True, "id": voucher.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    # Auto generate voucher number preview
    voucher_no = generate_voucher_no()

    return render(request, "accounts/voucher_create.html", {
        "voucher_types": voucher_types,
        "branches":      branches,
        "main_branch":   main_branch,
        "voucher_no":    voucher_no,
        "today":         today,
    })


@login_required
def voucher_edit(request, pk):
    voucher       = get_object_or_404(Voucher, id=pk)
    items         = voucher.items.all()
    voucher_types = VoucherType.objects.all().order_by("code")

    if request.method == "POST":
        try:
            data            = json.loads(request.body)
            voucher_type_id = data.get("voucher_type_id") or None
            narration       = data.get("narration", "")
            bill_ref_no     = data.get("bill_ref_no", "")
            new_items       = data.get("items", [])

            if not new_items:
                return JsonResponse({"success": False, "error": "Please add at least one entry."})

            total_amount = sum(float(i.get("amount", 0)) for i in new_items)

            voucher.voucher_type_id = voucher_type_id
            voucher.narration       = narration
            voucher.bill_ref_no     = bill_ref_no
            voucher.total_amount    = total_amount
            voucher.save()

            # Delete old items and recreate
            voucher.items.all().delete()

            for item in new_items:
                account_name = item.get("account_name", "")
                description  = item.get("description", "")
                debit_credit = item.get("debit_credit", "debit")
                amount       = float(item.get("amount", 0))

                if not account_name or amount <= 0:
                    continue

                VoucherItem.objects.create(
                    voucher_id   = voucher.id,
                    account_name = account_name,
                    description  = description,
                    debit_credit = debit_credit,
                    amount       = amount,
                )

            return JsonResponse({"success": True, "id": voucher.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return render(request, "accounts/voucher_edit.html", {
        "voucher":       voucher,
        "items":         items,
        "voucher_types": voucher_types,
    })


@login_required
def voucher_detail(request, pk):
    voucher = get_object_or_404(Voucher, id=pk)
    items   = voucher.items.all()
    return render(request, "accounts/voucher_detail.html", {
        "voucher": voucher,
        "items":   items,
    })


@login_required
def voucher_delete(request, pk):
    voucher = get_object_or_404(Voucher, id=pk)
    if request.method == "POST":
        voucher.delete()
        messages.success(request, "Voucher deleted.")
    return redirect("voucher_list")


# NEW VIEWS START HERE

@login_required
def cash_payment_voucher(request):
    cp_type  = VoucherType.objects.filter(code="CP").first()
    vouchers = Voucher.objects.filter(
        voucher_type=cp_type
    ).select_related(
        "branch", "voucher_type", "created_by"
    ).order_by("-created_at")

    return render(request, "accounts/cash_payment_voucher.html", {
        "vouchers": vouchers,
        "cp_type":  cp_type,
    })


@login_required
def cash_received_voucher(request):
    cr_type = VoucherType.objects.filter(code="CR").first()
    vouchers = Voucher.objects.filter(
        voucher_type=cr_type
    ).select_related(
        "branch", "voucher_type", "created_by"
    ).order_by("-created_at")

    return render(request, "accounts/cash_received_voucher.html", {
        "vouchers":vouchers,
        "cr_type":cr_type
    })



@login_required
def bank_payment_voucher(request):
    bp_type = VoucherType.objects.filter(code="BP").first()
    vouchers = Voucher.objects.filter(
        voucher_type= bp_type
    ).select_related(
        "branch", "voucher_type", "created_by"
    ).order_by("-created_at")

    return render(request, "accounts/bank_payment_voucher.html",{
        "vouchers": vouchers,
        "bp_type":bp_type
    })
    


@login_required
def bank_received_voucher(request):
    br_type = VoucherType.objects.filter(code="BR").first()
    vouchers = Voucher.objects.filter(
        voucher_type = br_type
    ).select_related(
        "branch", "voucher_type", "created_by"
    ).order_by("created_at")

    return render(request, "accounts/bank_received_voucher.html",{
        "br_type": br_type,
        "vouchers":vouchers
    })


@login_required
def chart_of_accounts(request):
    # Get all groups with their accounts
    groups   = AccountGroup.objects.select_related("parent").order_by("code")
    accounts = Account.objects.select_related("group").order_by("code")
    return render(request, "accounts/chart_of_accounts.html", {
        "groups":   groups,
        "accounts": accounts,
    })


# ── ADD ACCOUNT GROUP ─────────────────────────────────
@login_required
def add_account_group(request):
    groups = AccountGroup.objects.all().order_by("code")

    if request.method == "POST":
        name      = request.POST.get("name", "").strip().upper()
        code      = request.POST.get("code", "").strip()
        parent_id = request.POST.get("parent_id") or None

        if not name:
            messages.error(request, "Account group name is required.")
            return redirect("add_account_group")

        if AccountGroup.objects.filter(code=code).exists():
            messages.error(request, f"Code '{code}' already exists.")
            return redirect("add_account_group")

        AccountGroup.objects.create(
            name      = name,
            code      = code or None,
            parent_id = parent_id,
        )
        messages.success(request, f"Account group '{name}' created.")
        return redirect("chart_of_accounts")

    return render(request, "accounts/add_account_group.html", {
        "groups": groups,
    })


# ── ADD ACCOUNT ───────────────────────────────────────
@login_required
def add_account(request):
    groups = AccountGroup.objects.all().order_by("code")

    if request.method == "POST":
        name            = request.POST.get("name", "").strip().upper()
        code            = request.POST.get("code", "").strip()
        account_type    = request.POST.get("account_type", "asset")
        group_id        = request.POST.get("group_id") or None
        description     = request.POST.get("description", "")
        opening_balance = request.POST.get("opening_balance", 0)

        if not name:
            messages.error(request, "Account name is required.")
            return redirect("add_account")

        if code and Account.objects.filter(code=code).exists():
            messages.error(request, f"Code '{code}' already exists.")
            return redirect("add_account")

        Account.objects.create(
            name            = name,
            code            = code or None,
            account_type    = account_type,
            group_id        = group_id,
            description     = description,
            opening_balance = opening_balance or 0,
        )
        messages.success(request, f"Account '{name}' created.")
        return redirect("chart_of_accounts")

    return render(request, "accounts/add_account.html", {
        "groups": groups,
    })


# ── EDIT ACCOUNT ──────────────────────────────────────
@login_required
def edit_account(request, pk):
    account = get_object_or_404(Account, id=pk)
    groups  = AccountGroup.objects.all().order_by("code")

    if request.method == "POST":
        account.name            = request.POST.get("name", "").strip().upper()
        account.code            = request.POST.get("code", "").strip() or None
        account.account_type    = request.POST.get("account_type", "asset")
        account.group_id        = request.POST.get("group_id") or None
        account.description     = request.POST.get("description", "")
        account.opening_balance = request.POST.get("opening_balance", 0)
        account.save()
        messages.success(request, f"Account '{account.name}' updated.")
        return redirect("chart_of_accounts")

    return render(request, "accounts/edit_account.html", {
        "account": account,
        "groups":  groups,
    })


# ── DELETE ACCOUNT ────────────────────────────────────
@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, id=pk)
    if request.method == "POST":
        account.delete()
        messages.success(request, "Account deleted.")
    return redirect("chart_of_accounts")


# ── DELETE ACCOUNT GROUP ──────────────────────────────
@login_required
def delete_account_group(request, pk):
    group = get_object_or_404(AccountGroup, id=pk)
    if request.method == "POST":
        group.delete()
        messages.success(request, "Account group deleted.")
    return redirect("chart_of_accounts")


# ── ACCOUNT LEDGER ────────────────────────────────────
@login_required
def account_ledger(request, pk):
    account = get_object_or_404(Account, id=pk)
    entries = AccountLedgerEntry.objects.filter(
        account=account
    ).select_related("voucher").order_by("date", "created_at")

    # Calculate running balance
    running_balance = account.opening_balance
    entries_with_balance = []
    for entry in entries:
        if entry.debit_credit == "debit":
            running_balance += entry.amount
        else:
            running_balance -= entry.amount
        entries_with_balance.append({
            "entry":   entry,
            "balance": running_balance,
        })

    return render(request, "accounts/account_ledger.html", {
        "account":              account,
        "entries_with_balance": entries_with_balance,
        "closing_balance":      running_balance,
    })


##def chart_of_accounts(request):
    # render(request, "accounts/chart_of_accounts.html")


@login_required
def voucher_types(request):
    return render(request, "accounts/voucher_types.html")


@login_required
def credit_customers(request):
    return render(request, "accounts/credit_customers.html")
