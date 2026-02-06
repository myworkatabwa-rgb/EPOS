document.addEventListener("DOMContentLoaded", function () {

  /* ===============================
     STATE
  =============================== */
  let cart = [];

  /* ===============================
     DOM ELEMENTS (SAFE)
  =============================== */
  const cartItemsEl = document.getElementById("cart-items");
  const totalItemsEl = document.getElementById("total-items");
  const totalQtyEl = document.getElementById("total-qty");
  const subTotalEl = document.getElementById("sub-total");
  const totalEl = document.getElementById("total");
  const discountEl = document.getElementById("discount");
  const clearCartBtn = document.getElementById("clearCartBtn");
  const saveBookingBtn = document.getElementById("saveBookingBtn");
  const itemSearch = document.getElementById("itemSearch");

  /* ===============================
     ADD TO CART
  =============================== */
  document.querySelectorAll(".add-to-cart").forEach(btn => {
    btn.addEventListener("click", function () {
      const id = this.dataset.id;
      const name = this.dataset.name;
      const price = parseFloat(this.dataset.price);
      const sku = this.dataset.sku;

      const existing = cart.find(item => item.id === id);

      if (existing) {
        existing.qty += 1;
      } else {
        cart.push({
          id,
          sku,
          name,
          price,
          qty: 1
        });
      }

      renderCart();
    });
  });

  /* ===============================
     RENDER CART
  =============================== */
  function renderCart() {
    if (!cartItemsEl) return;

    if (cart.length === 0) {
      cartItemsEl.innerHTML = `<p class="text-muted">No items added</p>`;
      updateTotals();
      return;
    }

    cartItemsEl.innerHTML = "";

    cart.forEach((item, index) => {
      cartItemsEl.innerHTML += `
        <div class="d-flex justify-content-between align-items-center border-bottom py-1">
          <div>
            <strong>${item.name}</strong><br>
            <small>SKU: ${item.sku}</small>
          </div>
          <div class="text-end">
            <div>
              <button class="btn btn-sm btn-light minus-btn" data-index="${index}">−</button>
              <span class="mx-2">${item.qty}</span>
              <button class="btn btn-sm btn-light plus-btn" data-index="${index}">+</button>
            </div>
            <small>PKR ${item.price * item.qty}</small>
          </div>
        </div>
      `;
    });

    attachQtyEvents();
    updateTotals();
  }

  /* ===============================
     QTY BUTTONS
  =============================== */
  function attachQtyEvents() {
    document.querySelectorAll(".plus-btn").forEach(btn => {
      btn.addEventListener("click", function () {
        cart[this.dataset.index].qty++;
        renderCart();
      });
    });

    document.querySelectorAll(".minus-btn").forEach(btn => {
      btn.addEventListener("click", function () {
        const i = this.dataset.index;
        cart[i].qty--;
        if (cart[i].qty <= 0) cart.splice(i, 1);
        renderCart();
      });
    });
  }

  /* ===============================
     TOTALS
  =============================== */
  function updateTotals() {
    let totalItems = cart.length;
    let totalQty = 0;
    let subTotal = 0;

    cart.forEach(item => {
      totalQty += item.qty;
      subTotal += item.qty * item.price;
    });

    const discount = discountEl ? parseFloat(discountEl.value || 0) : 0;
    const total = Math.max(subTotal - discount, 0);

    if (totalItemsEl) totalItemsEl.innerText = totalItems;
    if (totalQtyEl) totalQtyEl.innerText = totalQty;
    if (subTotalEl) subTotalEl.innerText = subTotal.toFixed(0);
    if (totalEl) totalEl.innerText = total.toFixed(0);
  }

  if (discountEl) {
    discountEl.addEventListener("input", updateTotals);
  }

  /* ===============================
     CLEAR CART
  =============================== */
  if (clearCartBtn) {
    clearCartBtn.addEventListener("click", function () {
      if (!confirm("Discard booking?")) return;
      cart = [];
      renderCart();
    });
  }

  /* ===============================
     SAVE BOOKING (DEMO)
  =============================== */
  if (saveBookingBtn) {
    saveBookingBtn.addEventListener("click", function () {
      if (cart.length === 0) {
        alert("Cart is empty");
        return;
      }

      console.log("BOOKING DATA:", cart);

      const receiptModal = document.getElementById("receiptModal");
      if (receiptModal && window.bootstrap) {
        new bootstrap.Modal(receiptModal).show();
      }
    });
  }

  /* ===============================
     SEARCH ITEMS
  =============================== */
  if (itemSearch) {
    itemSearch.addEventListener("keyup", function () {
      const value = this.value.toLowerCase();
      document.querySelectorAll("#product-table-body tr").forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(value)
          ? ""
          : "none";
      });
    });
  }

});
