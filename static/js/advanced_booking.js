// =======================
// ADVANCED BOOKING SCRIPT
// =======================

let cart = {};
let discount = 0;
let totalAmount = 0;

// =======================
// DOM READY
// =======================
document.addEventListener("DOMContentLoaded", () => {

    // ADD TO CART
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            addToCart(
                btn.dataset.id,
                btn.dataset.name,
                btn.dataset.price
            );
        });
    });

    // SAVE BOOKING
    document.getElementById("saveBookingBtn")
        ?.addEventListener("click", saveBooking);

    // CLEAR CART
    document.getElementById("clearCartBtn")
        ?.addEventListener("click", clearCart);

    // DISCOUNT
    document.getElementById("discount")
        ?.addEventListener("input", renderCart);

    // RECEIPT BUTTONS
    document.getElementById("receiptOkBtn")?.addEventListener("click", () => {
        bootstrap.Modal.getInstance(
            document.getElementById("receiptModal")
        )?.hide();
    });

    document.getElementById("receiptPrintBtn")
        ?.addEventListener("click", () => window.print());

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
// SAVE BOOKING
// =======================
function saveBooking() {
    if (!Object.keys(cart).length) {
        alert("Cart is empty!");
        return;
    }

    fetch("/pos/booking/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            cart,
            discount,
            total: totalAmount
        })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            alert(data.error || "Booking failed");
            return;
        }

        showReceipt(data);
        clearCart();
    });
}

// =======================
// RECEIPT (REUSE SAME MODAL)
// =======================
function showReceipt(data) {
    let html = "";

    const items = data.items?.length
        ? data.items
        : Object.values(cart);

    items.forEach(i => {
        html += `
            <div class="d-flex justify-content-between">
                <span>${i.name} x ${i.qty}</span>
                <span>PKR ${(i.price * i.qty).toFixed(2)}</span>
            </div>
        `;
    });

    html += `
        <hr>
        <strong>Total: PKR ${(data.total ?? totalAmount).toFixed(2)}</strong>
    `;

    document.getElementById("receipt-body").innerHTML = html;

    new bootstrap.Modal(
        document.getElementById("receiptModal"),
        { backdrop: "static", keyboard: true }
    ).show();
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
// CSRF
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
