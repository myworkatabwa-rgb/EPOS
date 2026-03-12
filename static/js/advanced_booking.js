document.addEventListener("DOMContentLoaded", function () {
  let cart = [];

  const cartItemsEl  = document.getElementById("cart-items");
  const totalItemsEl = document.getElementById("total-items");
  const totalQtyEl   = document.getElementById("total-qty");
  const subTotalEl   = document.getElementById("sub-total");
  const totalEl      = document.getElementById("total");
  const discountEl   = document.getElementById("discount");
  const clearCartBtn = document.getElementById("clearCartBtn");
  const saveBtn      = document.getElementById("saveBookingBtn");
  const okBtn        = document.getElementById("receiptOkBtn");
  const printBtn     = document.getElementById("receiptPrintBtn");

  let receiptModal = null;
  let currentPackingNo = null;

  /* ===============================
     ADD TO CART
  =============================== */
  document.querySelectorAll(".add-to-cart").forEach(btn => {
    btn.addEventListener("click", function () {
      const id    = this.dataset.id;
      const name  = this.dataset.name;
      const price = parseFloat(this.dataset.price);
      const sku   = this.dataset.sku;

      const existing = cart.find(item => item.id === id);

      if (existing) {
        existing.qty++;
      } else {
        cart.push({ id, name, sku, price, qty: 1 });
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

    let html = "";

    cart.forEach((item, index) => {
      html += `
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

    cartItemsEl.innerHTML = html;
    attachQtyEvents();
    updateTotals();
  }

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
        if (cart[i].qty <= 0) cart.splice(i, 1);
        renderCart();
      };
    });
  }

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

  if (clearCartBtn) {
    clearCartBtn.addEventListener("click", function () {
      if (!confirm("Discard booking?")) return;
      cart = [];
      renderCart();
    });
  }

  /* ===============================
     AJAX SAVE + SHOW RECEIPT
  =============================== */
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      if (cart.length === 0) {
        alert("Cart is empty! Please add items first.");
        return;
      }

      const formData = new FormData();
      formData.append('cart_data', JSON.stringify(cart));
      formData.append('discount', discountEl.value || '0');
      formData.append('customer_id', document.getElementById('customer_id_input')?.value || '');

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken.value);
      }

      this.disabled = true;
      this.innerHTML = 'Saving...';

      fetch('', {
        method: 'POST',
        body: formData
      })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.success) {
          currentPackingNo = data.packing_no;
          showReceiptModal(parseFloat(discountEl.value || 0));
        } else {
          alert(data.error || 'Save failed');
        }
      })
      .catch(err => {
        console.error('Save error:', err);
        alert('Network error or save failed. Check console.');
      })
      .finally(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Save Booking';
      });
    });
  }

  /* ===============================
     SHOW RECEIPT MODAL
  =============================== */
  function showReceiptModal(discount) {
    const receiptBody = document.getElementById("receipt-body");
    if (!receiptBody) return;

    const now = new Date();
    const pad = n => String(n).padStart(2, "0");
    const dateStr = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
    const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const username = document.getElementById('pos-root')?.dataset?.username || 'Staff';

    let totalQty = 0;
    let totalItems = cart.length;
    let subTotal = 0;

    let html = `
      <div style="font-size:11px; margin-bottom:8px; line-height:1.8;">
        <div style="display:flex; justify-content:space-between;">
          <span>Packing No:</span><span><strong>${currentPackingNo || '—'}</strong></span>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Date:</span><span>${dateStr} ${timeStr}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Packed By:</span><span>${username}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Branch:</span><span>Main Branch</span>
        </div>
      </div>

      <div style="border-top:1px dashed #aaa; border-bottom:1px dashed #aaa; margin:6px 0; padding:4px 0;">
        <div style="display:grid; grid-template-columns:1fr auto auto auto; gap:4px; font-weight:bold; font-size:11px;">
          <span>Item</span>
          <span style="text-align:center;">Qty</span>
          <span style="text-align:right;">Price</span>
          <span style="text-align:right;">Total</span>
        </div>
      </div>
    `;

    cart.forEach(item => {
      const itemTotal = item.qty * item.price;
      totalQty += item.qty;
      subTotal += itemTotal;

      html += `
        <div style="margin-bottom:6px;">
          <div style="font-weight:600; font-size:12px;">${item.name}</div>
          <div style="display:grid; grid-template-columns:1fr auto auto auto; gap:4px; font-size:11px; color:#333;">
            <span style="color:#888;">SKU: ${item.sku || '—'}</span>
            <span style="text-align:center;">${item.qty}</span>
            <span style="text-align:right;">${item.price.toFixed(2)}</span>
            <span style="text-align:right;">${itemTotal.toFixed(2)}</span>
          </div>
        </div>
      `;
    });

    const netAmount = Math.max(subTotal - discount, 0);

    html += `
      <div style="border-top:1px dashed #aaa; margin-top:8px; padding-top:8px; font-size:11px; line-height:2;">
        <div style="display:flex; justify-content:space-between;">
          <span>Total Items/Qty:</span><span>${totalItems} / ${totalQty}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Sub Total:</span><span>Rs${subTotal.toFixed(2)}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:#c00;">
          <span>Discount:</span><span>- Rs${discount.toFixed(2)}</span>
        </div>
        <div style="border-top:1px dashed #aaa; margin-top:4px; padding-top:4px; display:flex; justify-content:space-between; font-size:14px; font-weight:bold;">
          <span>Net Amount:</span><span>Rs${netAmount.toFixed(2)}</span>
        </div>
      </div>

      <div style="text-align:center; margin-top:12px; font-size:10px; color:#888; border-top:1px dashed #ccc; padding-top:8px;">
        Thank you for your business!
      </div>
    `;

    receiptBody.innerHTML = html;

    receiptModal = new bootstrap.Modal(
      document.getElementById("receiptModal"),
      { backdrop: "static", keyboard: false }
    );
    receiptModal.show();
  }

  /* ===============================
     OK BUTTON - Clear cart & close
  =============================== */
  if (okBtn) {
    okBtn.addEventListener("click", function () {
      cart = [];
      renderCart();

      if (receiptModal) {
        receiptModal.hide();
      }
    });
  }

  /* ===============================
     PRINT RECEIPT (CLEAN POPUP)
  =============================== */
  function printReceipt() {
    const receiptContent = document.getElementById("receipt-body").innerHTML;

    const printWindow = window.open('', '_blank', 'width=400,height=600');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Packing Slip</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            width: 80mm;
            font-family: monospace;
            font-size: 12px;
            color: #000;
            background: #fff;
            padding: 8px;
          }
          @media print {
            @page {
              size: 80mm auto;
              margin: 0;
            }
            body {
              width: 80mm;
              padding: 4px;
            }
          }
        </style>
      </head>
      <body>
        ${receiptContent}
        <script>
          window.onload = function() {
            setTimeout(() => {
              window.print();
              window.close();
            }, 300);
          };
        <\/script>
      </body>
      </html>
    `);
    printWindow.document.close();
  }

  if (printBtn) {
    printBtn.addEventListener("click", function () {
      printReceipt();
    });
  }

});