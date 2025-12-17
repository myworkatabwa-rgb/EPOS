let cart = {};

// Add product
function addToCart(id, name, price) {
    if (!cart[id]) {
        cart[id] = { name, price, qty: 1 };
    } else {
        cart[id].qty += 1;
    }
    renderCart();
}

// Render cart
function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    const totalSpan = document.getElementById("total");

    cartDiv.innerHTML = "";
    let total = 0;

    for (let id in cart) {
        let item = cart[id];
        let subtotal = item.price * item.qty;
        total += subtotal;

        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between mb-2">
                <span>${item.name} x ${item.qty}</span>
                <span>Rs ${subtotal}</span>
            </div>
        `;
    }

    totalSpan.innerText = total;
}

// Checkout
function checkout() {
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
        body: JSON.stringify(cart)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`Order ${data.order_id} placed successfully!`);
            cart = {};
            renderCart();
        } else {
            alert("Error: " + data.error);
        }
    });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
