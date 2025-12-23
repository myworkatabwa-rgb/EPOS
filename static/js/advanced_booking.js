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

    // RECEIPT OK
    document.getElementById("receiptOkBtn")
        ?.addEventListener("click", () => {
            bootstrap.Modal.getInstance(
                document.getElementById("receiptModal")
            )?.hide();
        });

    // PRINT
    document.getElementById("receiptPrintBtn")
        ?.addEventListener("click", () => window.print());
});

// =======================
// ADD TO CART
// =======================
function addToCart(id, name, price) {
    price = Number(price);

    if (cart[id]) {
        cart[id].qty++;
    } else {
        cart[id] = {
            id,
            name,
            price,
            qty: 1
        };
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
            <div class="d-flex justify-content-between">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${total.toFixed(2)}</span>
            </div>
        `;
    });

    discount = Number(
        document.getElementById("discount").value || 0
    );

    totalAmount = Math.max(subTotal - discount, 0);

    document.getElementById("sub-total").innerText = subTotal.toFixed(2);
    document.getElementById("total").innerText = totalAmount.toFixed(2);
    document.getElementById("total-qty").innerText = totalQty;
    document.getElementById("total-items").innerText =
        Object.keys(cart).length;

    if (!Object.keys(cart).length) {
        cartDiv.innerHTML = `<p class="text-muted">No items added</p>`;
    }
}

// =======================
// SAVE BOOKING
// =======================
function saveBooking() {
    if (Object.keys(cart).length === 0) {
        alert("Please add items before saving booking");
        return;
    }

    // Build receipt HTML
    let html = "";

    Object.values(cart).forEach(item => {
        html += `
            <div class="d-flex justify-content-between">
                <span>${item.name} x ${item.qty}</span>
                <span>PKR ${(item.price * item.qty).toFixed(2)}</span>
            </div>
        `;
    });

    html += `
        <hr>
        <strong>Total Booking Amount: PKR ${totalAmount.toFixed(2)}</strong>
    `;

    document.getElementById("receipt-body").innerHTML = html;

    // Show receipt modal
    new bootstrap.Modal(
        document.getElementById("receiptModal"),
        { backdrop: "static", keyboard: true }
    ).show();

    // Clear cart for next booking
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
