document.addEventListener("DOMContentLoaded", function () {

  /* ===============================
     GLOBAL CART
  =============================== */
  let cart = [];

  const cartItemsEl  = document.getElementById("cart-items");
  const totalItemsEl = document.getElementById("total-items");
  const totalQtyEl   = document.getElementById("total-qty");
  const subTotalEl   = document.getElementById("sub-total");
  const totalEl      = document.getElementById("total");
  const discountEl   = document.getElementById("discount");
  const clearCartBtn = document.getElementById("clearCartBtn");
  const saveForm     = document.getElementById("saveBookingForm");

  let receiptModal = null;

  /* ===============================
     ADD PRODUCT TO CART
  =============================== */
  document.querySelectorAll(".add-to-cart").forEach(btn => {

    btn.addEventListener("click", function () {

      const id    = this.dataset.id;
      const name  = this.dataset.name;
      const price = parseFloat(this.dataset.price);
      const sku   = this.dataset.sku;

      const existing = cart.find(item => item.id === id);

      if (existing) {
        existing.qty += 1;
      } else {
        cart.push({ id, name, sku, price, qty: 1 });
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
            <small>SKU: ${item.sku || "-"}</small>
          </div>

          <div class="text-end">

            <div>
              <button class="btn btn-sm btn-light minus-btn" data-index="${index}">−</button>
              <span class="mx-2">${item.qty}</span>
              <button class="btn btn-sm btn-light plus-btn" data-index="${index}">+</button>
            </div>

            <small>PKR ${(item.price * item.qty).toFixed(2)}</small>

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

      btn.onclick = function () {

        cart[parseInt(this.dataset.index)].qty++;

        renderCart();
      };

    });

    document.querySelectorAll(".minus-btn").forEach(btn => {

      btn.onclick = function () {

        const i = parseInt(this.dataset.index);

        cart[i].qty--;

        if (cart[i].qty <= 0) {
          cart.splice(i, 1);
        }

        renderCart();
      };

    });

  }

  /* ===============================
     TOTAL CALCULATION
  =============================== */
  function updateTotals() {

    let totalQty = 0;
    let subTotal = 0;

    cart.forEach(item => {

      totalQty += item.qty;
      subTotal += item.qty * item.price;

    });

    const discount = discountEl ? parseFloat(discountEl.value || 0) : 0;

    const total = Math.max(subTotal - discount, 0);

    if (totalItemsEl) totalItemsEl.innerText = cart.length;
    if (totalQtyEl)   totalQtyEl.innerText   = totalQty;
    if (subTotalEl)   subTotalEl.innerText   = subTotal.toFixed(2);
    if (totalEl)      totalEl.innerText      = total.toFixed(2);
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
     FORM SUBMIT
  =============================== */
  if (saveForm) {

    saveForm.addEventListener("submit", function (e) {

      e.preventDefault();

      if (cart.length === 0) {

        alert("Cart is empty");

        return;
      }

      const discount = discountEl ? parseFloat(discountEl.value || 0) : 0;

      document.getElementById("cart_data_input").value = JSON.stringify(cart);
      document.getElementById("discount_input").value  = discount;

      showReceiptModal(discount);

    });

  }

  /* ===============================
     RECEIPT MODAL
  =============================== */
  function showReceiptModal(discount) {

    const receiptBody = document.getElementById("receipt-body");

    if (!receiptBody) return;

    const now = new Date();

    const pad = n => String(n).padStart(2, "0");

    const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
    const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

    const billNo = Math.floor(10000 + Math.random() * 90000);

    let totalQty = 0;
    let totalAmount = 0;
    let rows = "";

    cart.forEach(item => {

      const itemTotal = item.qty * item.price;

      totalQty += item.qty;
      totalAmount += itemTotal;

      rows += `
        <tr>
          <td>${item.name}</td>
          <td style="text-align:center;">${item.qty}</td>
          <td style="text-align:center;">${item.sku || "-"}</td>
          <td style="text-align:right;">${item.price.toFixed(2)}</td>
          <td style="text-align:right;">${itemTotal.toFixed(2)}</td>
        </tr>
      `;

    });

    const netAmount = Math.max(totalAmount - discount, 0);

    receiptBody.innerHTML = `
      <div style="font-family:monospace;font-size:12px">

        Bill No : ${billNo}<br>
        Date : ${dateStr}<br>
        Time : ${timeStr}<br>

        <hr>

        <table style="width:100%">

          <thead>

            <tr>
              <th>Description</th>
              <th>Qty</th>
              <th>SKU</th>
              <th>Rate</th>
              <th>Amount</th>
            </tr>

          </thead>

          <tbody>${rows}</tbody>

        </table>

        <hr>

        Items : ${cart.length}<br>
        Qty   : ${totalQty}<br>

        <br>

        Sub Total : PKR ${totalAmount.toFixed(2)}<br>
        Discount  : PKR ${discount.toFixed(2)}<br>

        <strong>Net Total : PKR ${netAmount.toFixed(2)}</strong>

      </div>
    `;

    receiptModal = new bootstrap.Modal(
      document.getElementById("receiptModal"),
      { backdrop: "static", keyboard: false }
    );

    receiptModal.show();

  }

  /* ===============================
     OK BUTTON
  =============================== */
  const okBtn = document.getElementById("receiptOkBtn");

  if (okBtn) {

    okBtn.addEventListener("click", function () {

      if (receiptModal) {
        receiptModal.hide();
      }

      setTimeout(function () {

        saveForm.submit();

      }, 400);

    });

  }

  /* ===============================
     PRINT
  =============================== */
  const printBtn = document.getElementById("receiptPrintBtn");

  if (printBtn) {

    printBtn.addEventListener("click", function () {

      window.print();

    });

  }

});