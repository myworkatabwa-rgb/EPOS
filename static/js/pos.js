// =======================
// POS Cart Script (FINAL)
// =======================

let cart = {};
let discount = 0;
let selectedPaymentMode = "cash";
let totalAmount = 0;
let paymentStep = "IDLE"; // IDLE | PAYMENT_OPEN

// =======================
// DOM READY
// =======================
document.addEventListener("DOMContentLoaded", () => {

    // ADD TO CART
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            addToCart(btn.dataset.id, btn.dataset.name, btn.dataset.price);
        });
    });

    // PAY BUTTON
    document.getElementById("payBtn")?.addEventListener("click", handlePayFlow);

    // CONFIRM BUTTONS
    document.getElementById("confirmPayBtn")
        ?.addEventListener("click", () => completePayment(false));

    document.getElementById("confirmPrintBtn")
        ?.addEventListener("click", () => completePayment(true));

    // CLEAR CART
    document.getElementById("clearCartBtn")
        ?.addEventListener("click", clearCart);

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
        window.print();
    });

    // SHORTCUTS
    document.addEventListener("keydown", e => {
        if (e.key === "F7") {
            e.preventDefault();
            handlePayFlow();
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
function addToCart(id, name, price) {
    price = Number(price);
    cart[id] ? cart[id].qty++ : cart[id] = { id, name, price, qty: 1 };
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

        const paymentModalEl = document.getElementById("paymentModal");
        const paymentModal = bootstrap.Modal.getInstance(paymentModalEl);

        paymentModal?.hide();

        setTimeout(() => {
            // Pass backend items if present, else fallback to cart
            const itemsToShow = data.items && data.items.length ? data.items : Object.values(cart);

            // Add extra info for receipt
            const receiptData = {
                items: itemsToShow,
                total: data.total || totalAmount,
                bill_no: data.bill_no || "00001",
                user: data.user || "N/A",
                counter: data.counter || "0001"
            };

            showReceipt(receiptData);
            clearCart();
            paymentStep = "IDLE";
        }, 300);
    });
}

// =======================
// RECEIPT - NEW UI
// =======================
function showReceipt(data) {
    const now = new Date();

    const pad = n => (n < 10 ? "0" + n : n);
    const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
    const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

    const paymentType = selectedPaymentMode.charAt(0).toUpperCase() + selectedPaymentMode.slice(1);

    let totalQty = 0;
    let totalAmount = 0;

    let html = `
        <div style="font-family: monospace; font-size:12px; padding:10px;">
            <div style="text-align:center; margin-bottom:10px;">
                <div>Contact : 0339-3777786</div>
                <h5>Sales Receipt</h5>
            </div>

            <div>
                Bill No  :  ${data.bill_no}<br>
                Date & Time  :  ${dateStr} ${timeStr}<br>
                Payment Type  :  ${paymentType}<br>
                User  :  ${data.user}<br>
                Counter  :  ${data.counter}<br>
            </div>

            <hr>

            <table style="width:100%; font-size:12px; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="text-align:left;">Description</th>
                        <th style="text-align:center;">Qty</th>
                        <th style="text-align:right;">Rate</th>
                        <th style="text-align:right;">Amount (PKRs)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.items.forEach(i => {
        const itemTotal = i.price * i.qty;
        totalQty += i.qty;
        totalAmount += itemTotal;

        html += `
            <tr>
                <td>${i.name}</td>
                <td style="text-align:center;">${i.qty}</td>
                <td style="text-align:right;">${i.price.toFixed(2)}</td>
                <td style="text-align:right;">${itemTotal.toFixed(2)}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>

            <hr>
            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                <span>No Of Items: ${data.items.length}</span>
                <span>Total Qty: ${totalQty}</span>
                <span>${totalAmount.toFixed(2)}</span>
            </div>

            <div style="display:flex; justify-content:space-between;">
                <span>Total:</span>
                <span>${totalAmount.toFixed(2)}</span>
            </div>

            <div style="display:flex; justify-content:space-between;">
                <span>Cash Paid:</span>
                <span>${Number(document.getElementById("cashTendered")?.value || totalAmount).toFixed(2)}</span>
            </div>

            <div style="display:flex; justify-content:space-between;">
                <span>Cash Balance:</span>
                <span>${Math.max(Number(document.getElementById("cashTendered")?.value || totalAmount) - totalAmount,0).toFixed(2)}</span>
            </div>

            <div style="text-align:center; margin:10px 0;">
                <svg id="barcode"></svg>
                <div>${data.bill_no}</div>
            </div>

            <div style="text-align:center; font-size:10px; margin-top:10px;">
                Print Date: ${dateStr} Print Time: ${timeStr}<br>
                Powered by: ZHePOS
            </div>
        </div>
    `;

    document.getElementById("receipt-body").innerHTML = html;

    // Barcode generation using JsBarcode (include JsBarcode library in HTML)
    if (typeof JsBarcode !== "undefined") {
        JsBarcode("#barcode", data.bill_no, {
            format: "CODE128",
            lineColor: "#000",
            width: 2,
            height: 40,
            displayValue: false
        });
    }

    new bootstrap.Modal(
        document.getElementById("receiptModal"),
        { backdrop: "static", keyboard: true }
    ).show();
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
