from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ZH_pos.models import Voucher, VoucherItem, VoucherType, Branch


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
