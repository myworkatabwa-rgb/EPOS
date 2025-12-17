let cart = {};
let total = 0;

function addToCart(id, name, price) {
    if (cart[id]) {
        cart[id].qty += 1;
    } else {
        cart[id] = { name, price, qty: 1 };
    }
    renderCart();
}

function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    cartDiv.innerHTML = "";
    total = 0;

    for (let id in cart) {
        let item = cart[id];
        let itemTotal = item.qty * item.price;
        total += itemTotal;

        cartDiv.innerHTML += `
            <div class="cart-item">
                <span>${item.name} x ${item.qty}</span>
                <span>Rs ${itemTotal}</span>
            </div>
        `;
    }

    document.getElementById("total").innerText = total;
}
