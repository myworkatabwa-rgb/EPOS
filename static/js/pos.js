// =======================
// POS Cart Script (Clean)
// =======================

let cart = {};
let discount = 0;
let selectedPaymentMode = "cash";
let totalAmount = 0;

// -----------------------
// Add Product
// -----------------------
function addToCart(id, name, price) {
    price = Number(price);

    if (!cart[id]) {
        cart[id] = { id, name, price, qty: 1 };
    } else {
        cart[id].qty++;
    }
    renderCart();
}

// -----------------------
// Render Cart
// -----------------------
function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    cartDiv.innerHTML = "";

    let subTotal = 0;
    let totalQty = 0;

    Object.values(cart).forEach(item => {
        let itemTotal = item.price * item.qty;
        subTotal += itemTotal;
        totalQty += item.qty;

        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between">
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
}

// -----------------------
// Open Payment Modal
// -----------------------
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

// -----------------------
// Payment Mode Switch
// -----------------------
document.querySelectorAll(".payment-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".payment-btn").forEach(b => {
            b.classList.remove("btn-primary");
            b.classList.add("btn-secondary");
        });
        btn.classList.add("btn-primary");
        selectedPaymentMode = btn.dataset.mode;
    });
});

// -----------------------
// Calculate Return
// -----------------------
function calculateReturn() {
    let cash = Number(document.getElementById("cashTendered").value || 0);
    let change = cash - totalAmount;
    document.getElementById("returnCash").innerText = change > 0 ? change.toFixed(2) : 0;
}

// -----------------------
// Confirm Payment → Backend
// -----------------------
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
    });
}

// -----------------------
// Clear Cart
// -----------------------
function clearCart() {
    cart = {};
    discount = 0;
    document.getElementById("discount").value = 0;
    renderCart();
}

// -----------------------
// CSRF Helper
// -----------------------
function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        }
    });
    return cookieValue;
}
