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
                btn.dataset.price,
                btn.dataset.sku || "-"
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
function addToCart(id, name, price, sku) {
    price = Number(price);

    if (cart[id]) {
        cart[id].qty++;
    } else {
        cart[id] = {
            id,
            name,
            price,
            sku,
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
// SAVE BOOKING (WITH RECEIPT UI)
// =======================
function saveBooking() {
    if (Object.keys(cart).length === 0) {
        alert("Please add items before saving booking");
        return;
    }

    const now = new Date();
    const pad = n => (n < 10 ? "0" + n : n);

    const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
    const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

    const bookingNo = "BK-" + Date.now();
    let totalQty = 0;
    let html = `
        <div style="font-family: monospace; font-size:12px; padding:10px;">

            <div style="text-align:right; font-weight:bold; color:green;">
                Booking Saved ✅
            </div>

            <div style="text-align:center; margin-bottom:10px;">
                <div>Contact : 0313-6330101</div>
                <h5>Booking Receipt</h5>
            </div>

            <div>
                Booking No : ${bookingNo}<br>
                Date & Time : ${dateStr} ${timeStr}<br>
            </div>

            <hr>

            <table style="width:100%; font-size:12px;">
                <thead>
                    <tr>
                        <th align="left">Description</th>
                        <th align="center">Qty</th>
                        <th align="center">SKU</th>
                        <th align="right">Rate</th>
                        <th align="right">Amount</th>
                    </tr>
                </thead>
                <tbody>
    `;

    Object.values(cart).forEach(item => {
        const itemTotal = item.price * item.qty;
        totalQty += item.qty;

        html += `
            <tr>
                <td>${item.name}</td>
                <td align="center">${item.qty}</td>
                <td align="center">${item.sku}</td>
                <td align="right">${item.price.toFixed(2)}</td>
                <td align="right">${itemTotal.toFixed(2)}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>

            <hr>

            <div style="display:flex; justify-content:space-between;">
                <span>No Of Items: ${Object.keys(cart).length}</span>
                <span>Total Qty: ${totalQty}</span>
                <span><b>${totalAmount.toFixed(2)}</b></span>
            </div>

            <div style="display:flex; justify-content:space-between;">
                <span>Total Booking Amount:</span>
                <span>${totalAmount.toFixed(2)}</span>
            </div>

            <div style="text-align:center; margin-top:10px;">
                <svg id="barcode"></svg>
                <div>${bookingNo}</div>
            </div>

            <div style="text-align:center; font-size:10px;">
                Powered by: ZHePOS
            </div>
        </div>
    `;

    document.getElementById("receipt-body").innerHTML = html;

    if (typeof JsBarcode !== "undefined") {
        JsBarcode("#barcode", bookingNo, {
            format: "CODE128",
            width: 2,
            height: 40,
            displayValue: false
        });
    }

    new bootstrap.Modal(
        document.getElementById("receiptModal"),
        { backdrop: "static", keyboard: true }
    ).show();

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
