document.addEventListener("DOMContentLoaded", function () {

  let cart = [];

  const cartItemsEl = document.getElementById("cart-items");
  const totalItemsEl = document.getElementById("total-items");
  const totalQtyEl = document.getElementById("total-qty");
  const subTotalEl = document.getElementById("sub-total");
  const totalEl = document.getElementById("total");
  const discountEl = document.getElementById("discount");
  const clearCartBtn = document.getElementById("clearCartBtn");
  const saveBookingBtn = document.getElementById("saveBookingBtn");
  const itemSearch = document.getElementById("itemSearch");
  const receiptOkBtn = document.getElementById("receiptOkBtn");
  const receiptPrintBtn = document.getElementById("receiptPrintBtn");

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
        cart.push({ id, sku, name, price, qty: 1 });
      }

      renderCart();
    });
  });

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
    if (subTotalEl) subTotalEl.innerText = subTotal.toFixed(2);
    if (totalEl) totalEl.innerText = total.toFixed(2);
  }

  if (discountEl) discountEl.addEventListener("input", updateTotals);

  if (clearCartBtn) {
    clearCartBtn.addEventListener("click", function () {
      if (!confirm("Discard booking?")) return;
      cart = [];
      renderCart();
    });
  }

  /* ===============================
     PROFESSIONAL RECEIPT
  =============================== */
  if (saveBookingBtn) {
    saveBookingBtn.addEventListener("click", function () {

      if (cart.length === 0) {
        alert("Cart is empty");
        return;
      }

      const receiptBody = document.getElementById("receipt-body");
      if (!receiptBody) return;

      const now = new Date();
      const pad = n => (n < 10 ? "0" + n : n);
      const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
      const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
      const billNo = Math.floor(10000 + Math.random() * 90000);

      let totalQty = 0;
      let totalAmount = 0;

      let html = `
        <div style="font-family: monospace; font-size:12px; padding:10px;">

          <div>
            Bill No : ${billNo}<br>
            Date & Time : ${dateStr} ${timeStr}<br>
            Payment Type : Booking<br>
            User : admin<br>
            Counter : 0001
          </div>

          <hr>

          <table style="width:100%; font-size:12px;">
            <thead>
              <tr>
                <th style="text-align:left;">Description</th>
                <th style="text-align:center;">Qty</th>
                <th style="text-align:center;">SKU</th>
                <th style="text-align:right;">Rate</th>
                <th style="text-align:right;">Amount</th>
              </tr>
            </thead>
            <tbody>
      `;

      cart.forEach(item => {
        const itemTotal = item.qty * item.price;
        totalQty += item.qty;
        totalAmount += itemTotal;

        html += `
          <tr>
            <td>${item.name}</td>
            <td style="text-align:center;">${item.qty}</td>
            <td style="text-align:center;">${item.sku || "-"}</td>
            <td style="text-align:right;">${item.price.toFixed(2)}</td>
            <td style="text-align:right;">${itemTotal.toFixed(2)}</td>
          </tr>
        `;
      });

      html += `
            </tbody>
          </table>

          <hr>

          <div style="display:flex; justify-content:space-between; font-weight:bold;">
            <span>No Of Items: ${cart.length}</span>
            <span>Total Qty: ${totalQty}</span>
            <span>${totalAmount.toFixed(2)}</span>
          </div>

          <div style="text-align:center; margin:10px 0;">
            <svg id="barcode"></svg>
            <div>${billNo}</div>
          </div>

          <div style="text-align:center; font-size:10px;">
            Print Date: ${dateStr} ${timeStr}<br>
            Powered by: ZHePOS
          </div>

        </div>
      `;

      receiptBody.innerHTML = html;

      if (typeof JsBarcode !== "undefined") {
        JsBarcode("#barcode", billNo.toString(), {
          format: "CODE128",
          width: 2,
          height: 40,
          displayValue: false
        });
      }

      new bootstrap.Modal(document.getElementById("receiptModal"), {
        backdrop: "static",
        keyboard: true
      }).show();

    });
  }

  if (receiptOkBtn) {
    receiptOkBtn.addEventListener("click", function () {
      bootstrap.Modal.getInstance(document.getElementById("receiptModal"))?.hide();
    });
  }

  if (receiptPrintBtn) {
    receiptPrintBtn.addEventListener("click", function () {
      window.print();
    });
  }

});