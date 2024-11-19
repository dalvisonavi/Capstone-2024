// Add new item to the inventory
document.getElementById('inventoryForm').onsubmit = function (event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const itemData = {};
    formData.forEach((value, key) => {
        itemData[key] = value;
    });

    fetch(this.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(itemData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'item added successfully!') {
            addItemToTable(data.item);
            window.location.reload(); // Add the new item to the table
            this.reset(); // Reset the form fields
        } else {
            alert('Error adding item: ' + data.message);
        }
    })
    .catch(error =>{
        console.error('Error processing', error);
        alert('There was an error adding the item.');
    });
};  


// Function to add item to the inventory list in the UI
function addItemToTable(item) {
    const itemList = document.getElementById('itemList');
    const newRow = document.createElement('li');
    newRow.classList.add('table-row');
    newRow.setAttribute('data-id', item._id);

    newRow.innerHTML = `
        <div class="col col-1" data-label="Name">${item.name}</div>
        <div class="col col-2" data-label="Quantity">${item.quantity}</div>
        <div class="col col-3" data-label="Expiry Date">${item.expiry_date}</div>
        <div class="col col-4" data-label="Previous Stock">${item.previous_stock}</div>
        <div class="col col-5" data-label="Action">
            <button class="edit-btn" onclick="editItem('${item._id}', this)"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/></svg></button>
            <button class="delete-btn" onclick="deleteItem('${item._id}')"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/></svg></button>
        </div>
    `;

    itemList.appendChild(newRow);
}

function editItem(itemId, button) {
    const row = button.closest('.table-row'); // Get the parent row
    
    // Get the existing values from each cell
    const nameCell = row.querySelector('.col.col-1');
    const quantityCell = row.querySelector('.col.col-2');
    const expiryDateCell = row.querySelector('.col.col-3');
    const prevStockCell = row.querySelector('.col.col-4');

    // Store original values in case of cancel
    const originalName = nameCell.innerText;
    const originalQuantity = quantityCell.innerText;
    const originalExpiryDate = expiryDateCell.innerText;
    const originalPrevStock = prevStockCell.innerText;

    // Convert each cell's text content to input fields
    nameCell.innerHTML = `<input type="text" value="${originalName}" />`;
    quantityCell.innerHTML = `<input type="number" value="${originalQuantity}" />`;
    expiryDateCell.innerHTML = `<input type="date" value="${new Date(originalExpiryDate).toISOString().substring(0, 10)}" />`;
    prevStockCell.innerHTML = `<input type="number" value="${originalPrevStock}" />`;

    // Change the button text to 'Save' and set a save function on click
    button.innerText = 'Save';
    button.onclick = () => saveItem(itemId, button, originalName, originalQuantity, originalExpiryDate, originalPrevStock);
}

function saveItem(itemId, button, originalName, originalQuantity, originalExpiryDate, originalPrevStock) {
    const row = button.closest('.table-row');

    // Get the values from the input fields
    const name = row.querySelector('.col.col-1 input').value;
    const quantity = row.querySelector('.col.col-2 input').value;
    const expiryDate = row.querySelector('.col.col-3 input').value;
    const prevStock = row.querySelector('.col.col-4 input').value;
    
    // Send data to the server to update the item in the database
    fetch(`/update_item/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            quantity: quantity,
            expiryDate: expiryDate,
            prevStock: prevStock
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'item updated successfully!') {
            // If update is successful, update the table cells with new values
            row.querySelector('.col.col-1').innerText = name;
            row.querySelector('.col.col-2').innerText = quantity;
            row.querySelector('.col.col-3').innerText = new Date(expiryDate).toLocaleDateString();
            row.querySelector('.col.col-4').innerText = prevStock;

            // Change the button text back to 'Edit' and reset the onclick handler
            button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                </svg>
            `;
            button.onclick = () => editItem(itemId, button);

            alert(data.message);
        } else {
            alert(data.message);
        }
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the item.');
    });
}

// Function to delete an item
function deleteItem(_id) {
    if (confirm("Are you sure you want to delete this item?")) {
        fetch(`/delete_inventory/${_id}`, {
            method: 'DELETE',  // Ensure this is DELETE to match the Flask route
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Item deleted successfully!') {
                const row = document.querySelector(`.table-row[data-id="${_id}"]`);
                if (row) {
                    row.remove(); // Remove the item from the table
                }
                alert(data.message);
                window.location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the item.');
        });
    }
}

document.getElementById('bakedProductForm').onsubmit = function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const productData = {};
    formData.forEach((value, key) => {
        productData[key] = value;
    });

    // Disable submit button to prevent multiple submissions
    const submitButton = this.querySelector("button[type='submit']");
    submitButton.disabled = true;

    fetch(this.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Baked product added successfully!') {
            addBakedProductToTable(data.item);
            this.reset();
            alert('Baked product added successfully!');
        } else {
            alert('Error adding product: ' + data.message);
        }
        window.location.reload();
    })
    .catch(error => {
        console.error('Error processing:', error);
        alert('There was an error adding the product.');
    })
    .finally(() => {
        submitButton.disabled = false; // Re-enable submit button
    });
};

function addBakedProductToTable(product) {
    const productList = document.getElementById('bakedProductsList');
    const newRow = document.createElement('li');
    newRow.classList.add('table-row');
    newRow.setAttribute('data-id', product._id);
    newRow.innerHTML = `
    <div class="col col-1" data-label="Name">${product.name}</div>
    <div class="col col-2" data-label="Quantity">${product.quantity}</div>
    <div class="col col-3" data-label="Prep Date">${product.prepdate}</div>
    <div class="col col-4" data-label="Expiry Date">${product.expiry_date}</div>
    <div class="col col-5" data-label="Action">
        <button class="edit-btn" onclick="editBakedProduct('${product._id}', this)">Edit</button>
        <button class="delete-btn" onclick="deleteBakedProduct('${product._id}')">Delete</button>
    </div>
`;
    productList.appendChild(newRow);
}


function editBakedProduct(productId, button) {
    const row = button.closest('.table-row'); // Get the parent row
    
    // Get the existing values from each cell
    const nameCell = row.querySelector('.col.col-1');
    const quantityCell = row.querySelector('.col.col-2');
    const prepDateCell = row.querySelector('.col.col-3');
    const expiryDateCell = row.querySelector('.col.col-4');

    // Store original values in case of cancel
    const originalName = nameCell.innerText;
    const originalQuantity = quantityCell.innerText;
    const originalPrepDate = prepDateCell.innerText;
    const originalExpiryDate = expiryDateCell.innerText;

    nameCell.innerHTML = `<input type="text" value="${originalName}" />`;
    quantityCell.innerHTML = `<input type="number" value="${originalQuantity}" />`;
    prepDateCell.innerHTML = `<input type="date" value="${new Date(originalPrepDate).toISOString().substring(0, 10)}" />`;
    expiryDateCell.innerHTML = `<input type="date" value="${new Date(originalExpiryDate).toISOString().substring(0, 10)}" />`;

    // Convert each cell's text content to input fields
    button.innerHTML = 'Save';
    button.onclick = () => saveBakedProduct(productId, button, originalName, originalQuantity, originalPrepDate,  originalExpiryDate);
}

function saveBakedProduct(productId, button, originalName, originalQuantity, originalPrepDate, originalExpiryDate) {
    const row = button.closest('.table-row');

    // Get the values from the input fields
    const name = row.querySelector('.col.col-1 input').value;
    const quantity = row.querySelector('.col.col-2 input').value;
    const prepDate = row.querySelector('.col.col-3 input').value;
    const expiryDate = row.querySelector('.col.col-4 input').value;
    
    // Send data to the server to update the baked product in the database
    fetch(`/update_baked_product/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            quantity: quantity,
            prepdate: prepDate,
            expiry_date: expiryDate,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'baked product updated successfully!') {
            // If update is successful, update the table cells with new values
            row.querySelector('.col.col-1').innerText = name;
            row.querySelector('.col.col-2').innerText = quantity;
            row.querySelector('.col.col-3').innerText = new Date(prepDate).toLocaleDateString();
            row.querySelector('.col.col-4').innerText = new Date(expiryDate).toLocaleDateString();

            // Change the button text back to 'Edit' and reset the onclick handler
            button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                </svg>
            `;
            button.onclick = () => editBakedProduct(productId, button);

            alert(data.message);
        } else {
            alert(data.message);
        }
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the baked product.');
    });
}


function deleteBakedProduct(_id) {
    if (confirm("Are you sure you want to delete this product?")) {
        fetch(`/delete_baked_product/${_id}`, { 
            method: 'DELETE',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.message === 'Baked product deleted successfully!') {
                const row = document.querySelector(`.table-row[data-id="${_id}"]`);
                if (row) {
                    row.remove();
                }
                alert(data.message);
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error occurred during fetch:', error);
            alert('An error occurred while deleting the product. Please try again later.');
        });
    }
}

