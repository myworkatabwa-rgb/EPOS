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

  // IMPORTANT: Set your logo static URL here
  const LOGO_URL = "/static/media/logo-1.jpeg";

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
          showReceiptModal(parseFloat(discountEl.value || 0), data);
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
     BUILD RECEIPT HTML
  =============================== */
  function buildReceiptHTML(discount, data) {
    const now = new Date();
    const pad = n => String(n).padStart(2, "0");
    const dateStr = `${pad(now.getDate())}-${pad(now.getMonth()+1)}-${now.getFullYear()}`;
    const hr = now.getHours();
    const timeStr = `${pad(hr > 12 ? hr - 12 : hr)}:${pad(now.getMinutes())} ${hr >= 12 ? 'pm' : 'am'}`;
    const username = document.getElementById('pos-root')?.dataset?.username || 'Staff';

    const remainingBalance = data.remaining_balance || 0;
    const amountPaid = data.amount_paid || 0;

    let totalQty = 0;
    let totalItems = cart.length;
    let subTotal = 0;
    let itemRows = "";

    cart.forEach(item => {
      const itemDisc = item.discount || 0;
      const itemTotal = (item.qty * item.price) - itemDisc;
      totalQty += item.qty;
      subTotal += itemTotal;

      itemRows += `
        <tr>
          <td style="padding:3px 2px; font-size:10px; word-break:break-word;">${item.name}</td>
          <td style="text-align:center; padding:3px 2px; font-size:10px;">${item.qty}<br><span style="font-size:9px; color:#555;">Default</span></td>
          <td style="text-align:right; padding:3px 2px; font-size:10px;">${item.price.toFixed(2)}</td>
          <td style="text-align:right; padding:3px 2px; font-size:10px;">${itemDisc.toFixed(2)}</td>
          <td style="text-align:right; padding:3px 2px; font-size:10px;">${itemTotal.toFixed(2)}</td>
        </tr>
      `;
    });

    const netAmount = Math.max(subTotal - discount, 0);

    return `
      <div style="font-family: monospace; font-size:11px; padding:4px; width:100%;">

          <!-- LOGO -->
          <div style="text-align:center; margin-bottom:6px;">
              <img src="${LOGO_URL}" style="height:60px; object-fit:contain;" alt="Logo">
              <div style="border-bottom:1px solid #000; margin-top:6px;"></div>
          </div>

          <!-- CONTACT -->
          <div style="text-align:center; margin-bottom:6px; font-size:11px;">
              Contact : 0313-6330101
          </div>

          <!-- TITLE BOX -->
          <div style="border:1px solid #000; text-align:center; font-weight:bold; padding:4px; margin-bottom:8px; font-size:12px;">
              Packing Slip
          </div>

          <!-- BILL INFO -->
          <div style="font-size:10px; line-height:1.9; margin-bottom:6px;">
              <div><strong>Packing No :</strong> ${currentPackingNo || '—'}</div>
              <div><strong>Date &amp; Time :</strong> ${dateStr} ${timeStr}</div>
              <div><strong>Packed By :</strong> ${username}</div>
              <div><strong>Branch :</strong> Main Branch</div>
          </div>

          <div style="border-top:1px solid #000;"></div>

          <!-- ITEMS TABLE -->
          <table style="width:100%; border-collapse:collapse; margin-top:2px;">
              <thead>
                  <tr style="border-bottom:1px solid #000;">
                      <th style="text-align:left; padding:3px 2px; font-size:10px;">DESCRIPTION</th>
                      <th style="text-align:center; padding:3px 2px; font-size:10px;">QTY</th>
                      <th style="text-align:right; padding:3px 2px; font-size:10px;">RATE</th>
                      <th style="text-align:right; padding:3px 2px; font-size:10px;">DISC</th>
                      <th style="text-align:right; padding:3px 2px; font-size:10px;">AMOUNT<br>(PKRS)</th>
                  </tr>
              </thead>
              <tbody>${itemRows}</tbody>
          </table>

          <div style="border-top:1px solid #000; margin-top:2px;"></div>

          <!-- SUMMARY ROW -->
          <div style="display:flex; justify-content:space-between; font-size:10px; padding:4px 0; border-bottom:1px solid #000;">
              <span>No Of Items: ${totalItems}</span>
              <span>Total Qty: ${totalQty}</span>
              <span style="font-weight:bold;">${subTotal.toFixed(2)}</span>
          </div>

          <!-- TOTALS -->
          <div style="font-size:11px; margin-top:6px; line-height:2;">
              <div style="display:flex; justify-content:space-between;">
                  <span>Sub Total :</span>
                  <span>${subTotal.toFixed(2)}</span>
              </div>
              <div style="display:flex; justify-content:space-between; color:#c00;">
                  <span>Discount :</span>
                  <span>- ${discount.toFixed(2)}</span>
              </div>
              <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:12px;">
                  <span>Net Amount :</span>
                  <span>${netAmount.toFixed(2)}</span>
              </div>
              <div style="display:flex; justify-content:space-between; font-weight:bold; border-top:1px solid #000; padding-top:4px; margin-top:2px;">
                  <span>Amount Paid :</span>
                  <span>${amountPaid.toFixed(2)}</span>
              </div>
              <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:12px;">
                  <span>Remaining Balance :</span>
                  <span>${remainingBalance.toFixed(2)}</span>
              </div>
          </div>

          <!-- NOTE -->
          <div style="font-size:10px; margin-top:10px;">
              <strong>NOTE:</strong>
              <div style="border:1px solid #ccc; padding:3px; min-height:16px; font-size:10px; color:#555;">
                  Print Date: ${dateStr} &nbsp;&nbsp; Print Time: ${timeStr}
              </div>
          </div>

          <!-- FOOTER -->
          <div style="text-align:center; font-size:10px; margin-top:8px; border-top:1px dashed #ccc; padding-top:6px;">
              Powered by: <strong>ZHePOS</strong>
          </div>

      </div>
    `;
  }

  /* ===============================
     SHOW RECEIPT MODAL
  =============================== */
  function showReceiptModal(discount, data) {
    const receiptBody = document.getElementById("receipt-body");
    if (!receiptBody) return;

    receiptBody.innerHTML = buildReceiptHTML(discount, data);

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

    const printWindow = window.open('', '_blank', 'width=300,height=700');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Packing Slip</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            width: 58mm;
            font-family: monospace;
            font-size: 11px;
            color: #000;
            background: #fff;
            padding: 4px;
          }
          table { width: 100%; border-collapse: collapse; }
          th, td { padding: 2px 1px; }
          img { max-width: 100%; }
          @media print {
            @page { size: 58mm auto; margin: 0; }
            body { width: 58mm; padding: 2px; }
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
            }, 400);
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