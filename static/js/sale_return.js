let saleId = null;
let returnItems = [];

function fetchSale() {
    const billNo = document.getElementById("billNo").value.trim();
    const invoiceNo = document.getElementById("invoiceNo").value.trim();

    if (!billNo && !invoiceNo) {
        alert("Please enter a Bill No or Invoice No.");
        return;
    }

    fetch(`/returns/fetch-sale/?bill_no=${billNo}&invoice_no=${invoiceNo}`)
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            alert(data.error);
            return;
        }

        saleId = data.sale_id;
        returnItems = [];
        const tbody = document.getElementById("returnTable");
        tbody.innerHTML = "";

        data.items.forEach(item => {
            tbody.innerHTML += `
              <tr>
                <td>${item.barcode}</td>
                <td>${item.name}</td>
                <td>${item.qty}</td>
                <td>
                  <input type="number" min="0" max="${item.qty}" value="0"
                    oninput="updateReturnQty(${item.id}, this.value, ${item.qty})">
                </td>
                <td>${item.price}</td>
                <td>${item.total}</td>
              </tr>
            `;
        });
    })
    .catch(err => {
        alert("Failed to fetch sale. Please try again.");
        console.error(err);
    });
}

function updateReturnQty(saleItemId, qty, maxQty) {
    qty = parseInt(qty) || 0;
    maxQty = parseInt(maxQty) || 0;

    if (qty < 0) qty = 0;
    if (qty > maxQty) {
        alert(`Return quantity cannot exceed original quantity of ${maxQty}.`);
        qty = maxQty;
    }

    if (qty === 0) {
        returnItems = returnItems.filter(i => i.sale_item_id !== saleItemId);
        return;
    }

    const index = returnItems.findIndex(i => i.sale_item_id === saleItemId);
    if (index >= 0) {
        returnItems[index].qty = qty;
    } else {
        returnItems.push({ sale_item_id: saleItemId, qty: qty });
    }
}

function confirmReturn() {
    if (!saleId) {
        alert("Please fetch a bill first.");
        return;
    }

    if (returnItems.length === 0) {
        alert("Please enter return quantity for at least one item.");
        return;
    }

    const reason = prompt("Enter return reason (optional):", "POS Return") || "POS Return";

    fetch("/returns/confirm/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            sale_id: saleId,
            reason: reason,
            items: returnItems
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Sale returned successfully.");
            saleId = null;
            returnItems = [];
            document.getElementById("returnTable").innerHTML = "";
            document.getElementById("billNo").value = "";
            document.getElementById("invoiceNo").value = "";
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(err => {
        alert("Request failed. Please try again.");
        console.error(err);
    });
}

function getCookie(name) {
    let value = null;
    document.cookie.split(";").forEach(c => {
        c = c.trim();
        if (c.startsWith(name + "=")) {
            value = decodeURIComponent(c.substring(name.length + 1));
        }
    });
    return value;
}