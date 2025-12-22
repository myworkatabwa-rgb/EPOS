// =======================
// POS Cart Script (Clean)
// =======================

let cart = {};
let discount = 0;

// -----------------------
// Add Product to Cart
// -----------------------
function addToCart(id, name, price) {
    price = Number(price);

    if (!cart[id]) {
        cart[id] = {
            id: id,
            name: name,
            price: price,
            qty: 1
        };
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

    discount = parseFloat(document.getElementById("discount")?.value || 0);
    const grandTotal = Math.max(subTotal - discount, 0);

    document.getElementById("sub-total").innerText = subTotal.toFixed(2);
    document.getElementById("total").innerText = grandTotal.toFixed(2);
    document.getElementById("total-qty").innerText = totalQty;
    document.getElementById("total-items").innerText = Object.keys(cart).length;
}

// -----------------------
// Checkout
// -----------------------
function checkout(paymentMethod) {
    if (Object.keys(cart).length === 0) {
        alert("Cart is empty!");
        return;
    }

    fetch("/pos/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            cart: cart,
            discount: discount,
            payment_method: paymentMethod
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showReceipt(data);
            clearCart();
        } else {
            alert(data.error || "Checkout failed");
        }
    })
    .catch(() => alert("Server error!"));
}

// -----------------------
// Receipt Modal
// -----------------------
function showReceipt(data) {
    let html = "";

    data.items.forEach(item => {
        html += `<div>${item.name} x ${item.qty} - PKR ${item.total}</div>`;
    });

    document.getElementById("receipt-items").innerHTML = html;
    document.getElementById("receipt-total").innerText = data.total;
    document.getElementById("receipt-payment").innerText = data.payment_method;

    new bootstrap.Modal(document.getElementById("receiptModal")).show();
}

// -----------------------
// Clear Cart
// -----------------------
function clearCart() {
    cart = {};
    discount = 0;
    if (document.getElementById("discount")) {
        document.getElementById("discount").value = "";
    }
    renderCart();
}

// -----------------------
// Django CSRF Helper
// -----------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        document.cookie.split(";").forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}
