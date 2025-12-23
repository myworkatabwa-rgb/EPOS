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

        bootstrap.Modal.getInstance(document.getElementById("paymentModal"))?.hide();
        showReceipt(data);
        paymentStep = "IDLE";
    });
}

// =======================
// RECEIPT
// =======================
function showReceipt(data) {
    let html = "";
    data.items.forEach(i => {
        html += `
            <div class="d-flex justify-content-between">
                <span>${i.name} x ${i.qty}</span>
                <span>PKR ${(i.price * i.qty).toFixed(2)}</span>
            </div>
        `;
    });

    html += `<hr><strong>Total: PKR ${data.total.toFixed(2)}</strong>`;
    document.getElementById("receipt-body").innerHTML = html;

    new bootstrap.Modal(document.getElementById("receiptModal")).show();
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
