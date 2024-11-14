// Supplier Data (for dynamic display)
let suppliers = []; // Assume this will be populated from MongoDB or other sources

// Add Supplier Functionality
document.getElementById('supplierForm').addEventListener('submit', function(event) {
    console.log('Form is being submitted');
    
    // Get input values
    const name = document.getElementById('supplierName').value;
    const email = document.getElementById('supplierEmail').value;
    const phone = document.getElementById('supplierPhone').value;
    const products = document.getElementById('productsSupplied').value.split(',');

    // Log the values
    console.log('Form values:', {
        supplier_name: name,
        contact_email: email,
        contact_phone: phone,
        products: products
    });
});
function editSupplier(supplierId, button) {
    console.log(`Editing supplier with ID: ${supplierId}`);
    const row = button.closest('.table-row'); // Get the closest row
    console.log('Row:', row);

    // Extract the cells
    const supplierNameCell = row.querySelector('.col-1');
    const supplierEmailCell = row.querySelector('.col-2');
    const supplierPhoneCell = row.querySelector('.col-3');
    const productsCell = row.querySelector('.col-4');

    // Store original values for use in saveSupplier
    const originalName = supplierNameCell.innerText;
    const originalEmail = supplierEmailCell.innerText;
    const originalPhone = supplierPhoneCell.innerText;
    const originalProducts = productsCell.innerText.split(', ');

    // Create input fields for editing
    supplierNameCell.innerHTML = `<input type="text" value="${originalName}" />`;
    supplierEmailCell.innerHTML = `<input type="email" value="${originalEmail}" />`;
    supplierPhoneCell.innerHTML = `<input type="text" value="${originalPhone}" />`;
    productsCell.innerHTML = `<input type="text" value="${originalProducts.join(', ')}" />`;

    // Change the button to Save
    button.innerText = 'Save';
    button.onclick = () => saveSupplier(supplierId, button, originalName, originalEmail, originalPhone, originalProducts.join(', '));
}

function saveSupplier(supplierId, button, originalName, originalEmail, originalPhone, originalProducts) {
    const row = button.closest('.table-row'); // Get the closest row containing the data
    const supplierName = row.querySelector('.col-1 input').value;
    const supplierEmail = row.querySelector('.col-2 input').value;
    const supplierPhone = row.querySelector('.col-3 input').value;
    const products = row.querySelector('.col-4 input').value.split(',').map(product => product.trim());

    // Log the new values being sent to the server
    console.log('Saving supplier:', {
        supplierId: supplierId,
        supplier_name: supplierName,
        contact_email: supplierEmail,
        contact_phone: supplierPhone,
        products: products
    });

    // Validate input
    if (!supplierName || !supplierEmail || !supplierPhone || products.length === 0) {
        alert('All fields are required!');
        return;
    }

    // Make the PUT request to update the supplier
    fetch(`/update_supplier/${supplierId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            supplier_name: supplierName,
            contact_email: supplierEmail,
            contact_phone: supplierPhone,
            products: products
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Supplier updated successfully!') {
            // Update the table cells with new values
            row.querySelector('.col-1').innerText = supplierName;
            row.querySelector('.col-2').innerText = supplierEmail;
            row.querySelector('.col-3').innerText = supplierPhone;
            row.querySelector('.col-4').innerText = products.join(', ');

            // Change the button back to Edit
           // Change the button back to the original Edit button with icon and functionality
button.innerHTML = `
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
</svg>
`;
button.onclick = () => editSupplier(supplierId, button);


            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the supplier.');
    });
}

function deleteSupplier(supplierId) {
    console.log(`Attempting to delete supplier with ID: ${supplierId}`);
    if (confirm('Are you sure you want to delete this supplier?')) {
        fetch(`/delete_supplier/${supplierId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Supplier deleted successfully!') {
                // Remove the supplier row from the list
                const row = document.querySelector(`.table-row[data-id="${supplierId}"]`);
                if (row) {
                    row.remove();
                }
                alert(data.message);
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the supplier.');
        });
    }
}


function triggerOrder(productId) {
    fetch(`/trigger_order/${productId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message && data.message.includes('successfully')) {
            alert("Order triggered successfully!");
        } else {
            alert("Failed to trigger order.");
        }
    })
    .catch(error => console.error("Error:", error));
}
