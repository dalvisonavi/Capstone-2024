function bakedaddItem() {
    const itemName = document.getElementById("name").value;
    const itemQuantity = document.getElementById("quantity").value;
    const itemexpirydate = document.getElementById("expirydate").value;
    const itemprepdate = document.getElementById("prepdate").value;
    const itemdoneby = document.getElementById("doneby").value;

    // Check if inputs are valid
    if (itemName === "" || itemQuantity === "" || itemexpirydate=== ""||itemprepdate=== ""|| itemdoneby==="") {
        alert("Please enter item name, quantity and expirydate.");
        return;
    }

    // Create an object with the data
    const data = {
        name: itemName,
        quantity: parseInt(itemQuantity),
        expirydate: Date(itemexpirydate),
        prepdate: Date(itemprepdate),
        doneby: itemdoneby
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
        bakedfetchItems();
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function bakedfetchItems() {
    
}
