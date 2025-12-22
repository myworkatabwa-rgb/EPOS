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
        confirmPayBtn.addEventListener("click", () => handlePayment(false));
    }

    if (confirmPrintBtn) {
        confirmPrintBtn.addEventListener("click", () => handlePayment(true));
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

    // RECEIPT MODAL BUTTONS
    document.getElementById("receiptOkBtn")?.addEventListener("click", () => {
        bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
    });
    document.getElementById("receiptPrintBtn")?.addEventListener("click", () => {
        window.print();
    });

    // SHORTCUT KEYS
    document.addEventListener("keydown", function(e){
        if(e.key === "F7"){ e.preventDefault(); payBtn?.click(); }
        if(e.key === "F9"){ 
            e.preventDefault();
            const receiptModal = bootstrap.Modal.getInstance(document.getElementById("receiptModal"));
            if(receiptModal) document.getElementById("receiptPrintBtn")?.click();
            else confirmPrintBtn?.click();
        }
        if(e.key === "Escape"){
            const paymentModal = bootstrap.Modal.getInstance(document.getElementById("paymentModal"));
            if(paymentModal) paymentModal.hide();
            const receiptModal = bootstrap.Modal.getInstance(document.getElementById("receiptModal"));
            if(receiptModal) receiptModal.hide();
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

    new bootstrap.Modal(document.getElementById("paymentModal")).show();
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

    // Show relevant input
    document.querySelectorAll(".cash-mode, .card-mode, .party-mode, .split-mode")
        .forEach(el => el.classList.add("d-none"));

    if (selectedPaymentMode === "cash") document.querySelector(".cash-mode")?.classList.remove("d-none");
    if (selectedPaymentMode === "card") document.querySelector(".card-mode")?.classList.remove("d-none");
    if (selectedPaymentMode === "party") document.querySelector(".party-mode")?.classList.remove("d-none");
    if (selectedPaymentMode === "split") document.querySelector(".split-mode")?.classList.remove("d-none");
}

// =======================
// CALCULATE RETURN CASH
// =======================
function calculateReturn() {
    const cash = Number(document.getElementById("cashTendered")?.value || 0);
    const change = cash - totalAmount;

    document.getElementById("returnCash").innerText =
        change > 0 ? change.toFixed(2) : "0.00";
}

// =======================
// CONFIRM PAYMENT → BACKEND
// =======================
function confirmPayment(print = false) {
    if(Object.keys(cart).length === 0){
        alert("Cart is empty!");
        return Promise.reject("Cart empty");
    }

    return fetch("/pos/checkout/", {
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
            print,
            cash_received: selectedPaymentMode === "card" 
                            ? Number(document.querySelector(".card-mode input[type='number']")?.value || 0)
                            : undefined
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            clearCart();
            return data; // Return data for receipt modal
        } else {
            alert(data.error || "Payment failed");
            return Promise.reject(data.error || "Payment failed");
        }
    })
    .catch(err => {
        alert(err || "Server error!");
        return Promise.reject(err);
    });
}

// =======================
// HANDLE PAYMENT & SHOW RECEIPT
// =======================
function handlePayment(print=false){
    confirmPayment(print).then(data=>{
        const receiptBody = document.getElementById("receipt-body");
        let html = "";
        data.items.forEach(item=>{
            html += `<div>${item.name} x ${item.qty} - PKR ${(item.price * item.qty).toFixed(2)}</div>`;
        });
        html += `<hr><strong>Total: PKR ${data.total.toFixed(2)}</strong>`;
        receiptBody.innerHTML = html;

        new bootstrap.Modal(document.getElementById("receiptModal")).show();
    }).catch(()=>{ /* payment failed or cart empty */ });
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
