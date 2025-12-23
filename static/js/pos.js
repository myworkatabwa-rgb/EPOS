// =======================
// POS Cart Script (FINAL)
// CSP SAFE – NO INLINE JS
// =======================

let cart = {};
let discount = 0;
let selectedPaymentMode = "cash";
let totalAmount = 0;

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
    document.getElementById("payBtn")?.addEventListener("click", openPaymentModal);

    // CONFIRM PAYMENT
    document.getElementById("confirmPayBtn")
        ?.addEventListener("click", () => handlePayment(false));

    document.getElementById("confirmPrintBtn")
        ?.addEventListener("click", () => handlePayment(true));

    // CLEAR CART (ONLY PLACE THAT CLEARS)
    document.getElementById("clearCartBtn")
        ?.addEventListener("click", clearCart);

    // PAYMENT MODE SWITCH
    document.querySelectorAll(".payment-btn").forEach(btn => {
        btn.addEventListener("click", () => switchPaymentMode(btn));
    });

    // DISCOUNT
    document.getElementById("discount")
        ?.addEventListener("input", renderCart);

    // CASH INPUT
    document.getElementById("cashTendered")
        ?.addEventListener("input", calculateReturn);

    // RECEIPT BUTTONS
    document.getElementById("receiptOkBtn")?.addEventListener("click", () => {
        bootstrap.Modal.getInstance(
            document.getElementById("receiptModal")
        )?.hide();
    });

    document.getElementById("receiptPrintBtn")?.addEventListener("click", () => {
        window.print();
    });

    // SHORTCUT KEYS
    document.addEventListener("keydown", e => {
        if (e.key === "F7") {
            e.preventDefault();
            const modalOpen = document.getElementById("paymentModal")
                ?.classList.contains("show");

            if (modalOpen) {
                document.getElementById("confirmPayBtn")?.click();
            } else {
                document.getElementById("payBtn")?.click();
            }
        }

        if (e.key === "F9") {
            e.preventDefault();
            const receiptOpen = document.getElementById("receiptModal")
                ?.classList.contains("show");

            if (receiptOpen) {
                document.getElementById("receiptPrintBtn")?.click();
            } else {
                document.getElementById("confirmPrintBtn")?.click();
            }
        }

        if (e.key === "Escape") {
            bootstrap.Modal.getInstance(
                document.getElementById("paymentModal")
            )?.hide();

            bootstrap.Modal.getInstance(
                document.getElementById("receiptModal")
            )?.hide();
        }
    });

});

// =======================
// ADD TO CART
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
    cartDiv.innerHTML = "";

    let subTotal = 0;
    let totalQty = 0;

    Object.values(cart).forEach(item => {
        const total = item.price * item.qty;
        subTotal += total;
        totalQty += item.qty;

        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between mb-1">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${total.toFixed(2)}</span>
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

    document.querySelectorAll(
        ".cash-mode, .card-mode, .party-mode, .split-mode"
    ).forEach(el => el.classList.add("d-none"));

    document.querySelector(`.${selectedPaymentMode}-mode`)
        ?.classList.remove("d-none");
}

// =======================
// CASH RETURN
// =======================
function calculateReturn() {
    const cash = Number(
        document.getElementById("cashTendered")?.value || 0
    );
    document.getElementById("returnCash").innerText =
        Math.max(cash - totalAmount, 0).toFixed(2);
}

// =======================
// CONFIRM PAYMENT (NO CLEAR)
// =======================
function confirmPayment(print = false) {
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
// HANDLE PAYMENT + RECEIPT
// =======================
function handlePayment(print = false) {
    if (Object.keys(cart).length === 0) {
        alert("Cart is empty!");
        return;
    }

    confirmPayment(print).then(data => {
        if (!data.success) {
            alert(data.error || "Payment failed");
            return;
        }

        bootstrap.Modal.getInstance(
            document.getElementById("paymentModal")
        )?.hide();

        let html = "";
        data.items.forEach(i => {
            html += `
                <div class="d-flex justify-content-between">
                    <span>${i.name} x ${i.qty}</span>
                    <span>PKR ${(i.price * i.qty).toFixed(2)}</span>
                </div>
            `;
        });

        html += `
            <hr>
            <strong>Total: PKR ${data.total.toFixed(2)}</strong>
        `;

        document.getElementById("receipt-body").innerHTML = html;

        new bootstrap.Modal(
            document.getElementById("receiptModal")
        ).show();
    });
}

// =======================
// CLEAR CART (MANUAL ONLY)
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
