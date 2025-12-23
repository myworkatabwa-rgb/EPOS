// =======================
// POS Cart Script (FINAL)
// CSP SAFE – NO INLINE JS
// =======================

let cart = {};
let discount = 0;
let selectedPaymentMode = "cash";
let totalAmount = 0;

// =======================
// DOM READY BINDINGS
// =======================
document.addEventListener("DOMContentLoaded", () => {

    // PAY BUTTON (F7)
    const payBtn = document.getElementById("payBtn");
    if (payBtn) payBtn.addEventListener("click", openPaymentModal);

    // CONFIRM PAYMENT BUTTONS
    const confirmPayBtn = document.getElementById("confirmPayBtn");
    const confirmPrintBtn = document.getElementById("confirmPrintBtn");

    if (confirmPayBtn) confirmPayBtn.addEventListener("click", () => handlePayment(false));
    if (confirmPrintBtn) confirmPrintBtn.addEventListener("click", () => handlePayment(true));

    // PAYMENT MODE SWITCH
    document.querySelectorAll(".payment-btn").forEach(btn => {
        btn.addEventListener("click", () => switchPaymentMode(btn));
    });

    // DISCOUNT CHANGE
    document.getElementById("discount")?.addEventListener("input", renderCart);

    // CASH TENDERED CHANGE
    document.getElementById("cashTendered")?.addEventListener("input", calculateReturn);

    // RECEIPT BUTTONS
    document.getElementById("receiptOkBtn")?.addEventListener("click", closeReceiptAndReset);
    document.getElementById("receiptPrintBtn")?.addEventListener("click", () => {
        window.print();
        closeReceiptAndReset();
    });

    // SHORTCUT KEYS
    document.addEventListener("keydown", e => {
        if (e.key === "F7") {
            e.preventDefault();
            payBtn?.click();
        }
        if (e.key === "F9") {
            e.preventDefault();
            document.getElementById("receiptPrintBtn")?.click();
        }
        if (e.key === "Escape") {
            bootstrap.Modal.getInstance(document.getElementById("paymentModal"))?.hide();
            bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
        }
    });

    // ADD TO CART
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            addToCart(btn.dataset.id, btn.dataset.name, btn.dataset.price);
        });
    });

    // CLEAR CART
    document.getElementById("clearCartBtn")?.addEventListener("click", clearCart);
});

// =======================
// ADD PRODUCT
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
    if (!cartDiv) return;

    cartDiv.innerHTML = "";
    let subTotal = 0, totalQty = 0;

    Object.values(cart).forEach(item => {
        const itemTotal = item.price * item.qty;
        subTotal += itemTotal;
        totalQty += item.qty;

        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between mb-1">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${itemTotal.toFixed(2)}</span>
            </div>`;
    });

    discount = Number(document.getElementById("discount")?.value || 0);
    totalAmount = Math.max(subTotal - discount, 0);

    document.getElementById("sub-total").innerText = subTotal.toFixed(2);
    document.getElementById("total").innerText = totalAmount.toFixed(2);
    document.getElementById("total-qty").innerText = totalQty;
    document.getElementById("total-items").innerText = Object.keys(cart).length;

    if (!Object.keys(cart).length) {
        cartDiv.innerHTML = `<p class="text-muted">No items added</p>`;
    }
}

// =======================
// OPEN PAYMENT MODAL
// =======================
function openPaymentModal() {
    if (!Object.keys(cart).length) {
        alert("Cart is empty!");
        return;
    }

    document.getElementById("payTotal").innerText = totalAmount.toFixed(2);
    document.getElementById("cashTendered").value = totalAmount;
    calculateReturn();

    new bootstrap.Modal(document.getElementById("paymentModal")).show();
}

// =======================
// PAYMENT MODE SWITCH
// =======================
function switchPaymentMode(btn) {
    document.querySelectorAll(".payment-btn").forEach(b => {
        b.classList.replace("btn-primary", "btn-secondary");
        b.classList.remove("active");
    });

    btn.classList.replace("btn-secondary", "btn-primary");
    btn.classList.add("active");
    selectedPaymentMode = btn.dataset.mode;

    document.querySelectorAll(".cash-mode,.card-mode,.party-mode,.split-mode")
        .forEach(el => el.classList.add("d-none"));

    document.querySelector(`.${selectedPaymentMode}-mode`)?.classList.remove("d-none");
}

// =======================
// CALCULATE RETURN CASH
// =======================
function calculateReturn() {
    const cash = Number(document.getElementById("cashTendered")?.value || 0);
    document.getElementById("returnCash").innerText =
        Math.max(cash - totalAmount, 0).toFixed(2);
}

// =======================
// CONFIRM PAYMENT → BACKEND
// =======================
function confirmPayment(print = false) {
    if (!Object.keys(cart).length) return Promise.reject("Empty cart");

    return fetch("/pos/checkout/", {
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
    }).then(res => res.json());
}

// =======================
// HANDLE PAYMENT & RECEIPT
// =======================
function handlePayment(print) {
    confirmPayment(print).then(data => {
        if (!data.success) throw data.error;

        bootstrap.Modal.getInstance(document.getElementById("paymentModal"))?.hide();

        const receiptBody = document.getElementById("receipt-body");
        receiptBody.innerHTML = data.items.map(i =>
            `<div>${i.name} x ${i.qty} — PKR ${(i.qty * i.price).toFixed(2)}</div>`
        ).join("") + `<hr><strong>Total: PKR ${data.total.toFixed(2)}</strong>`;

        new bootstrap.Modal(document.getElementById("receiptModal")).show();
    }).catch(err => alert(err || "Payment failed"));
}

// =======================
// CLOSE RECEIPT & RESET
// =======================
function closeReceiptAndReset() {
    bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
    clearCart();
}

// =======================
// CLEAR CART
// =======================
function clearCart() {
    cart = {};
    discount = 0;
    document.getElementById("discount").value = 0;
    renderCart();
}

// =======================
// CSRF TOKEN
// =======================
function getCookie(name) {
    return document.cookie.split("; ").find(c => c.startsWith(name + "="))
        ?.split("=")[1] || null;
}
