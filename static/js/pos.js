// =======================
// Simple POS Cart Script
// =======================

let cart = {};

// Add product to cart
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
        cart[id].qty += 1;
    }

    renderCart();
}

// Render cart items
function renderCart() {
    const cartDiv = document.getElementById("cart-items");
    const totalSpan = document.getElementById("total");

    if (!cartDiv || !totalSpan) return;

    cartDiv.innerHTML = "";
    let total = 0;

    Object.values(cart).forEach(item => {
        const subtotal = item.price * item.qty;
        total += subtotal;

        const row = document.createElement("div");
        row.className = "d-flex justify-content-between mb-2";
        row.innerHTML = `
            <span>${item.name} x ${item.qty}</span>
            <span>Rs ${subtotal.toFixed(2)}</span>
        `;
        cartDiv.appendChild(row);
    });

    totalSpan.innerText = total.toFixed(2);
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Order ${data.order_id} placed successfully!`);
            cart = {};
            renderCart();
        } else {
            alert(data.error || "Checkout failed");
        }
    })
    .catch(() => {
        alert("Server error!");
    });
}

// Django CSRF helper
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
function showReceipt(data) {
    let html = "";
    data.items.forEach(i => {
        html += `<div>${i.name} x ${i.qty} - PKR ${i.total}</div>`;
    });

    document.getElementById("receipt-items").innerHTML = html;
    document.getElementById("receipt-total").innerText = data.total;
    document.getElementById("receipt-payment").innerText = data.payment_method;

    new bootstrap.Modal(document.getElementById("receiptModal")).show();
}
let cart = {};
let discount = 0;

function addToCart(id, name, price) {
  if (!cart[id]) {
    cart[id] = { name, price, qty: 1 };
  } else {
    cart[id].qty++;
  }
  renderCart();
}

function renderCart() {
  const cartDiv = document.getElementById("cart-items");
  cartDiv.innerHTML = "";
  let total = 0;
  let qty = 0;

  Object.values(cart).forEach(item => {
    total += item.price * item.qty;
    qty += item.qty;

    cartDiv.innerHTML += `
      <div class="d-flex justify-content-between">
        <span>${item.name} x ${item.qty}</span>
        <span>PKR ${item.price * item.qty}</span>
      </div>
    `;
  });

  discount = parseFloat(document.getElementById("discount").value || 0);

  document.getElementById("total").innerText = total - discount;
  document.getElementById("sub-total").innerText = total;
  document.getElementById("total-qty").innerText = qty;
  document.getElementById("total-items").innerText = Object.keys(cart).length;
}

function checkout(method) {
  fetch("/pos/checkout/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify({
      cart: cart,
      discount: discount,
      payment_method: method
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Sale completed");
      cart = {};
      renderCart();
    }
  });
}

function clearCart() {
  cart = {};
  renderCart();
}

function getCookie(name) {
  let cookieValue = null;
  document.cookie.split(";").forEach(c => {
    c = c.trim();
    if (c.startsWith(name + "=")) {
      cookieValue = decodeURIComponent(c.substring(name.length + 1));
    }
  });
  return cookieValue;
}


