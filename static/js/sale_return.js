let saleId = null;
let returnItems = [];

function fetchSale() {
    const billNo = document.getElementById("billNo").value;
    const invoiceNo = document.getElementById("invoiceNo").value;

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
                  <input type="number" min="0" max="${item.qty}"
                    onchange="updateReturnQty(${item.id}, this.value)">
                </td>
                <td>${item.price}</td>
                <td>${item.total}</td>
              </tr>
            `;
        });
    });
}

function updateReturnQty(saleItemId, qty) {
    const index = returnItems.findIndex(i => i.sale_item_id === saleItemId);
    if (index >= 0) {
        returnItems[index].qty = qty;
    } else {
        returnItems.push({ sale_item_id: saleItemId, qty });
    }
}

function confirmReturn() {
    fetch("/returns/confirm/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            sale_id: saleId,
            items: returnItems
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Sale returned successfully");
            location.reload();
        } else {
            alert(data.error);
        }
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
