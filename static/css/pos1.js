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
// Category filters code

document.addEventListener("DOMContentLoaded", function () {

  let currentCategory = "all";

  const categoryButtons = document.querySelectorAll(".category-btn");
  const rows = document.querySelectorAll("#product-table-body tr");
  const searchInput = document.getElementById("itemSearch");

  // Category Click
  categoryButtons.forEach(btn => {
    btn.addEventListener("click", function () {

      categoryButtons.forEach(b => b.classList.remove("active"));
      this.classList.add("active");

      currentCategory = this.dataset.category;
      filterProducts();
    });
  });

  // Search (barcode or name)
  searchInput.addEventListener("keyup", function () {
    filterProducts();
  });

  function filterProducts() {
    const searchValue = searchInput.value.toLowerCase();

    rows.forEach(row => {
      const sku = row.cells[0].innerText.toLowerCase();
      const name = row.cells[2].innerText.toLowerCase();
      const category = row.dataset.category;

      const matchCategory = (currentCategory === "all" || category === currentCategory);
      const matchSearch = sku.includes(searchValue) || name.includes(searchValue);

      if (matchCategory && matchSearch) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

});
