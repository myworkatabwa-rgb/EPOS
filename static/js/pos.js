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
    if (payBtn) {
        payBtn.addEventListener("click", openPaymentModal);
    }

    // CONFIRM PAYMENT BUTTONS
    const confirmPayBtn = document.getElementById("confirmPayBtn");
    const confirmPrintBtn = document.getElementById("confirmPrintBtn");

    if (confirmPayBtn) {
        confirmPayBtn.addEventListener("click", () => confirmPayment(false));
    }

    if (confirmPrintBtn) {
        confirmPrintBtn.addEventListener("click", () => confirmPayment(true));
    }

    // PAYMENT MODE SWITCH
    document.querySelectorAll(".payment-btn").forEach(btn => {
        btn.addEventListener("click", () => switchPaymentMode(btn));
    });

    // DISCOUNT CHANGE
    const discountInput = document.getElementById("discount");
    if (discountInput) {
        discountInput.addEventListener("input", renderCart);
    }

    // CASH TENDERED CHANGE
    const cashInput = document.getElementById("cashTendered");
    if (cashInput) {
        cashInput.addEventListener("input", calculateReturn);
    }
});

// =======================
// ADD PRODUCT
// =======================
function addToCart(id, name, price) {
    price = Number(price);

    if (!cart[id]) {
        cart[id] = { id, name, price, qty: 1 };
    } else {
        cart[id].qty++;
    }
    renderCart();
}

// =======================
// RENDER CART
// =======================
function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    if (!cartDiv) return;

    cartDiv.innerHTML = "";

    let subTotal = 0;
    let totalQty = 0;

    Object.values(cart).forEach(item => {
        const itemTotal = item.price * item.qty;
        subTotal += itemTotal;
        totalQty += item.qty;

        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between mb-1">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${itemTotal.toFixed(2)}</span>
            </div>
        `;
    });

    discount = Number(document.getElementById("discount")?.value || 0);
    totalAmount = Math.max(subTotal - discount, 0);

    document.getElementById("sub-total").innerText = subTotal.toFixed(2);
    document.getElementById("total").innerText = totalAmount.toFixed(2);
    document.getElementById("total-qty").innerText = totalQty;
    document.getElementById("total-items").innerText = Object.keys(cart).length;

    if (Object.keys(cart).length === 0) {
        cartDiv.innerHTML = `<p class="text-muted">No items added</p>`;
    }
}

// =======================
// OPEN PAYMENT MODAL
// =======================
function openPaymentModal() {
    if (Object.keys(cart).length === 0) {
        alert("Cart is empty!");
        return;
    }

    document.getElementById("payTotal").innerText = totalAmount.toFixed(2);
    document.getElementById("cashTendered").value = totalAmount;
    calculateReturn();

    new bootstrap.Modal(
        document.getElementById("paymentModal")
    ).show();
}

// =======================
// PAYMENT MODE SWITCH
// =======================
function switchPaymentMode(btn) {
    document.querySelectorAll(".payment-btn").forEach(b => {
        b.classList.remove("btn-primary", "active");
        b.classList.add("btn-secondary");
    });

    btn.classList.remove("btn-secondary");
    btn.classList.add("btn-primary", "active");
    selectedPaymentMode = btn.dataset.mode;
}

// =======================
// CALCULATE RETURN CASH
// =======================
function calculateReturn() {
    const cash = Number(document.getElementById("cashTendered").value || 0);
    const change = cash - totalAmount;

    document.getElementById("returnCash").innerText =
        change > 0 ? change.toFixed(2) : "0.00";
}

// =======================
// CONFIRM PAYMENT → BACKEND
// =======================
function confirmPayment(print = false) {
    fetch("/pos/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            cart,
            discount,
            payment_mode: selectedPaymentMode,
            total: totalAmount,
            print
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            clearCart();
            alert("Payment Successful!");

            bootstrap.Modal.getInstance(
                document.getElementById("paymentModal")
            ).hide();
        } else {
            alert(data.error || "Payment failed");
        }
    })
    .catch(() => alert("Server error!"));
}

// =======================
// CLEAR CART
// =======================
function clearCart() {
    cart = {};
    discount = 0;

    const discountInput = document.getElementById("discount");
    if (discountInput) discountInput.value = 0;

    renderCart();
}

// =======================
// CSRF TOKEN HELPER
// =======================
function getCookie(name) {
    let cookieValue = null;

    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
            );
        }
    });
    return cookieValue;
}
