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
    const row = button.parentElement.parentElement; // Get the row containing the buttons
    console.log('Row:',row);
    const supplierNameCell = row.cells[0];
    const supplierEmailCell = row.cells[1];
    const supplierPhoneCell = row.cells[2];
    const productsCell = row.cells[3];

    // Store the original values
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
    button.setAttribute('onclick', `saveSupplier('${supplierId}', this, '${originalName}', '${originalEmail}', '${originalPhone}', '${originalProducts.join(', ')}')`);
}

function saveSupplier(supplierId, button, originalName, originalEmail, originalPhone, originalProducts) {
    
    const row = button.parentElement.parentElement; // Get the row containing the buttons
    const supplierName = row.cells[0].querySelector('input').value;
    const supplierEmail = row.cells[1].querySelector('input').value;
    const supplierPhone = row.cells[2].querySelector('input').value;
    const products = row.cells[3].querySelector('input').value.split(',');

    // log the new values being sent to the server
    console.log('saving supplier:',{
        supplierId: supplierId,
        supplier_name: supplierName,
        contact_email: supplierEmail,
        contact_phone: supplierPhone,
        products: products
    });
    // Validate input
    if (!supplierName || !supplierEmail || !supplierPhone || !products.length) {
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
            row.cells[0].innerText = supplierName;
            row.cells[1].innerText = supplierEmail;
            row.cells[2].innerText = supplierPhone;
            row.cells[3].innerText = products.join(', ');

            // Change the button back to Edit
            button.innerText = 'Edit';
            button.setAttribute('onclick', `editSupplier('${supplierId}', this)`);
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
    console.log(`Attempting to delete supplier with ID: ${supplierId}`); // Use backticks here
    if (confirm('Are you sure you want to delete this supplier?')) {
        fetch(`/delete_supplier/${supplierId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Supplier deleted successfully!') {
                // Remove the supplier row from the table
                const row = document.querySelector(`tr[data-id="${supplierId}"]`);
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
