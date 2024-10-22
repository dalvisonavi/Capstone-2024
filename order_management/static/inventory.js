function addItem() {
    const itemName = document.getElementById("name").value;
    const itemQuantity = document.getElementById("quantity").value;
    const itemexpirydate = document.getElementById("expirydate").value;
    const itemprevStock = document.getElementById("prevStock").value;

    // Check if inputs are valid
    if (itemName === "" || itemQuantity === "" || itemexpirydate=== ""||itemprevStock==="") {
        alert("Please enter item name, quantity and expirydate.");
        return;
    }

    // Create an object with the data
    const data = {
        name: itemName,
        quantity: parseInt(itemQuantity),
        expirydate: Date(itemexpirydate),
        prevStock: itemprevStock
    };


    fetch("/add_items", {
        method: "POST",
        headers: {
            "Content-Type": "application/json", 
        },
        body: JSON.stringify(data), 
    })
    
    .then(response => response.json())
    .then(result => {    
        document.getElementById("message").innerText = result.message;
        fetchItems();
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function fetchItems() {
    
}
