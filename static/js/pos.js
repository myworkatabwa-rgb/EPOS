// =======================
// POS Cart Script (FINAL UPDATED)
// =======================

let cart = {};
let discount = 0;
let selectedPaymentMode = "cash";
let totalAmount = 0;
let paymentStep = "IDLE"; // IDLE | PAYMENT_OPEN

// Get logged-in user from HTML dataset
const loggedInUser = document.getElementById('pos-root')?.dataset.username || 'N/A';

// IMPORTANT: Set your logo static URL here
const LOGO_URL = "/static/media/logo-1.jpeg";

// =======================
// DOM READY
// =======================
document.addEventListener("DOMContentLoaded", () => {

    // ADD TO CART
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            addToCart(btn.dataset.id, btn.dataset.name, btn.dataset.price, btn.dataset.sku);
        });
    });

    // PAY BUTTON
    document.getElementById("payBtn")?.addEventListener("click", handlePayFlow);

    // CONFIRM BUTTONS
    document.getElementById("confirmPayBtn")?.addEventListener("click", () => completePayment(false));
    document.getElementById("confirmPrintBtn")?.addEventListener("click", () => completePayment(true));

    // CLEAR CART
    document.getElementById("clearCartBtn")?.addEventListener("click", clearCart);

    // PAYMENT MODE
    document.querySelectorAll(".payment-btn").forEach(btn => {
        btn.addEventListener("click", () => switchPaymentMode(btn));
    });

    // INPUTS
    document.getElementById("discount")?.addEventListener("input", renderCart);
    document.getElementById("cashTendered")?.addEventListener("input", calculateReturn);

    // RECEIPT BUTTONS
    document.getElementById("receiptOkBtn")?.addEventListener("click", () => {
        bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
        paymentStep = "IDLE";
    });

    document.getElementById("receiptPrintBtn")?.addEventListener("click", () => {
        printReceipt();
    });

    // SHORTCUTS
    document.addEventListener("keydown", e => {
        if (e.key === "F7") {
            e.preventDefault();
            handlePayFlow();
        }

        if (e.key === "F8") {
            e.preventDefault();
            const receiptModal = document.getElementById("receiptModal");
            if (receiptModal && receiptModal.classList.contains("show")) {
                printReceipt();
            }
        }

        if (e.key === "Escape") {
            bootstrap.Modal.getInstance(document.getElementById("paymentModal"))?.hide();
            bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
            paymentStep = "IDLE";
        }
    });
});

// =======================
// PAY FLOW CONTROLLER
// =======================
function handlePayFlow() {
    if (Object.keys(cart).length === 0) {
        alert("Cart is empty!");
        return;
    }

    if (paymentStep === "IDLE") {
        openPaymentModal();
        paymentStep = "PAYMENT_OPEN";
    } else if (paymentStep === "PAYMENT_OPEN") {
        completePayment(false);
    }
}

// =======================
// ADD TO CART
// =======================
function addToCart(id, name, price, sku) {
    price = Number(price);
    if (cart[id]) {
        cart[id].qty++;
    } else {
        cart[id] = { id, name, price, sku, qty: 1 };
    }
    renderCart();
}

// =======================
// RENDER CART
// =======================
function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    cartDiv.innerHTML = "";

    let subTotal = 0, totalQty = 0;

    Object.values(cart).forEach(item => {
        const t = item.price * item.qty;
        subTotal += t;
        totalQty += item.qty;
        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${t.toFixed(2)}</span>
            </div>
        `;
    });

    discount = Number(document.getElementById("discount").value || 0);
    totalAmount = Math.max(subTotal - discount, 0);

    document.getElementById("sub-total").innerText = subTotal.toFixed(2);
    document.getElementById("total").innerText = totalAmount.toFixed(2);
    document.getElementById("total-qty").innerText = totalQty;
    document.getElementById("total-items").innerText = Object.keys(cart).length;

    if (!Object.keys(cart).length)
        cartDiv.innerHTML = `<p class="text-muted">No items added</p>`;
}

// =======================
// PAYMENT MODAL
// =======================
function openPaymentModal() {
    document.getElementById("payTotal").innerText = totalAmount.toFixed(2);
    document.getElementById("cashTendered").value = totalAmount;
    calculateReturn();

    new bootstrap.Modal(document.getElementById("paymentModal")).show();
}

// =======================
// COMPLETE PAYMENT
// =======================
function completePayment(print) {
    fetch("/pos/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            cart,
            discount,
            total: totalAmount,
            payment_mode: selectedPaymentMode,
            print
        })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            alert(data.error || "Payment failed");
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("paymentModal"))?.hide();

        setTimeout(() => {
            const itemsToShow = data.items && data.items.length ? data.items : Object.values(cart);

            const receiptData = {
                items: itemsToShow,
                total: data.total || totalAmount,
                bill_no: data.bill_no || "00001",
                user: data.user || loggedInUser,
                counter: data.counter || "0001",
                remaining_balance: data.remaining_balance || 0
            };

            showReceipt(receiptData);
            clearCart();
            paymentStep = "IDLE";
        }, 300);
    });
}

// =======================
// BUILD RECEIPT HTML
// =======================
function buildReceiptHTML(data, cashPaid) {
    const now = new Date();
    const pad = n => (n < 10 ? "0" + n : n);
    const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
    const hr = now.getHours();
    const timeStr = `${pad(hr > 12 ? hr - 12 : hr)}:${pad(now.getMinutes())} ${hr >= 12 ? 'pm' : 'am'}`;
    const paymentType = selectedPaymentMode.charAt(0).toUpperCase() + selectedPaymentMode.slice(1);

    const remainingBalance = data.remaining_balance || Math.max((data.total || 0) - cashPaid, 0);

    let totalQty = 0;
    let calcTotal = 0;
    let itemRows = "";

    data.items.forEach(i => {
        const itemDisc = i.discount || 0;
        const itemTotal = (i.price * i.qty) - itemDisc;
        totalQty += i.qty;
        calcTotal += itemTotal;

        itemRows += `
            <tr>
                <td style="padding:3px 2px; font-size:10px; word-break:break-word;">${i.name}</td>
                <td style="text-align:center; padding:3px 2px; font-size:10px;">${i.qty}<br><span style="font-size:9px; color:#555;">Default</span></td>
                <td style="text-align:right; padding:3px 2px; font-size:10px;">${i.price.toFixed(2)}</td>
                <td style="text-align:right; padding:3px 2px; font-size:10px;">${itemDisc.toFixed(2)}</td>
                <td style="text-align:right; padding:3px 2px; font-size:10px;">${itemTotal.toFixed(2)}</td>
            </tr>
        `;
    });

    return `
        <div style="font-family: monospace; font-size:11px; padding:4px; width:100%;">

            <!-- LOGO -->
            <div style="text-align:center; margin-bottom:6px;">
                <img src="${LOGO_URL}" style="height:60px; object-fit:contain;" alt="Logo">
                <div style="border-bottom:1px solid #000; margin-top:6px;"></div>
            </div>

            <!-- CONTACT -->
            <div style="text-align:center; margin-bottom:6px; font-size:11px;">
                Contact : 0313-6330101
            </div>

            <!-- TITLE BOX -->
            <div style="border:1px solid #000; text-align:center; font-weight:bold; padding:4px; margin-bottom:8px; font-size:12px;">
                Sales Receipt
            </div>

            <!-- BILL INFO -->
            <div style="font-size:10px; line-height:1.9; margin-bottom:6px;">
                <div><strong>Bill No :</strong> ${data.bill_no}</div>
                <div><strong>Date &amp; Time :</strong> ${dateStr} ${timeStr}</div>
                <div><strong>Payment Type :</strong> ${paymentType}</div>
                <div><strong>User :</strong> ${data.user}</div>
                <div><strong>Counter :</strong> ${data.counter}</div>
            </div>

            <div style="border-top:1px solid #000;"></div>

            <!-- ITEMS TABLE -->
            <table style="width:100%; border-collapse:collapse; margin-top:2px;">
                <thead>
                    <tr style="border-bottom:1px solid #000;">
                        <th style="text-align:left; padding:3px 2px; font-size:10px;">DESCRIPTION</th>
                        <th style="text-align:center; padding:3px 2px; font-size:10px;">QTY</th>
                        <th style="text-align:right; padding:3px 2px; font-size:10px;">RATE</th>
                        <th style="text-align:right; padding:3px 2px; font-size:10px;">DISC</th>
                        <th style="text-align:right; padding:3px 2px; font-size:10px;">AMOUNT<br>(PKRS)</th>
                    </tr>
                </thead>
                <tbody>${itemRows}</tbody>
            </table>

            <div style="border-top:1px solid #000; margin-top:2px;"></div>

            <!-- SUMMARY ROW -->
            <div style="display:flex; justify-content:space-between; font-size:10px; padding:4px 0; border-bottom:1px solid #000;">
                <span>No Of Items: ${data.items.length}</span>
                <span>Total Qty: ${totalQty}</span>
                <span style="font-weight:bold;">${calcTotal.toFixed(2)}</span>
            </div>

            <!-- TOTALS -->
            <div style="font-size:11px; margin-top:6px; line-height:2;">
                <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:12px;">
                    <span>Total :</span>
                    <span>${calcTotal.toFixed(2)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span>Paid via ${paymentType} :</span>
                    <span>${cashPaid.toFixed(2)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:12px; border-top:1px solid #000; padding-top:4px; margin-top:2px;">
                    <span>Remaining Balance :</span>
                    <span>${remainingBalance.toFixed(2)}</span>
                </div>
            </div>

            <!-- BARCODE -->
            <div style="text-align:center; margin:10px 0 4px;">
                <svg id="barcode" data-bill="${data.bill_no}"></svg>
                <div style="font-size:11px; margin-top:2px;">${data.bill_no}</div>
            </div>

            <!-- NOTE -->
            <div style="font-size:10px; margin-top:6px;">
                <strong>NOTE:</strong>
                <div style="border:1px solid #ccc; padding:3px; min-height:16px; font-size:10px; color:#555;">
                    Print Date: ${dateStr} &nbsp;&nbsp; Print Time: ${timeStr}
                </div>
            </div>

            <!-- FOOTER -->
            <div style="text-align:center; font-size:10px; margin-top:8px; border-top:1px dashed #ccc; padding-top:6px;">
                Powered by: <strong>ZHePOS</strong>
            </div>

        </div>
    `;
}

// =======================
// SHOW RECEIPT MODAL
// =======================
function showReceipt(data) {
    const cashPaid = Number(document.getElementById("cashTendered")?.value || 0);
    document.getElementById("receipt-body").innerHTML = buildReceiptHTML(data, cashPaid);

    if (typeof JsBarcode !== "undefined") {
        JsBarcode("#barcode", data.bill_no, {
            format: "CODE128",
            lineColor: "#000",
            width: 1.5,
            height: 50,
            displayValue: false
        });
    }

    new bootstrap.Modal(
        document.getElementById("receiptModal"),
        { backdrop: "static", keyboard: true }
    ).show();
}

// =======================
// PRINT RECEIPT (CLEAN POPUP)
// =======================
function printReceipt() {
    const receiptContent = document.getElementById("receipt-body").innerHTML;

    const printWindow = window.open('', '_blank', 'width=300,height=700');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sales Receipt</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"><\/script>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body {
                    width: 58mm;
                    font-family: monospace;
                    font-size: 11px;
                    color: #000;
                    background: #fff;
                    padding: 4px;
                }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 2px 1px; }
                img { max-width: 100%; }
                svg { display: block; margin: 0 auto; }
                @media print {
                    @page { size: 58mm auto; margin: 0; }
                    body { width: 58mm; padding: 2px; }
                }
            </style>
        </head>
        <body>
            ${receiptContent}
            <script>
                window.onload = function() {
                    if (typeof JsBarcode !== 'undefined') {
                        const svg = document.querySelector('#barcode');
                        const billNo = svg?.getAttribute('data-bill') || '00001';
                        JsBarcode("#barcode", billNo, {
                            format: "CODE128",
                            lineColor: "#000",
                            width: 1.5,
                            height: 50,
                            displayValue: false
                        });
                    }
                    setTimeout(() => {
                        window.print();
                        window.close();
                    }, 400);
                };
            <\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

// =======================
// PAYMENT MODE
// =======================
function switchPaymentMode(btn) {
    document.querySelectorAll(".payment-btn").forEach(b => {
        b.classList.remove("btn-primary");
        b.classList.add("btn-secondary");
    });

    btn.classList.add("btn-primary");
    selectedPaymentMode = btn.dataset.mode;

    document.querySelectorAll(".cash-mode,.card-mode,.party-mode,.split-mode")
        .forEach(e => e.classList.add("d-none"));

    document.querySelector(`.${selectedPaymentMode}-mode`)?.classList.remove("d-none");
}

// =======================
function calculateReturn() {
    const cash = Number(document.getElementById("cashTendered").value || 0);
    document.getElementById("returnCash").innerText =
        Math.max(cash - totalAmount, 0).toFixed(2);
}

// =======================
function clearCart() {
    cart = {};
    discount = 0;
    document.getElementById("discount").value = 0;
    renderCart();
}

// =======================
function getCookie(name) {
    let v = null;
    document.cookie.split(";").forEach(c => {
        c = c.trim();
        if (c.startsWith(name + "="))
            v = decodeURIComponent(c.substring(name.length + 1));
    });
    return v;
}