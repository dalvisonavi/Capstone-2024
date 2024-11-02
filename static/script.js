
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("rawMaterialsButton").addEventListener("click", function () {
        window.location.href = "/rawmaterials";
    });

    document.getElementById("bakedMaterialsButton").addEventListener("click", function () {
        window.location.href ="/bakedmaterials";
    });
});


// Function to load HTML content into the dynamicContent div
function loadPage(page) {
    fetch(page)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.text();
        })
        .then(data => {
            document.getElementById("dynamicContent").innerHTML = data;
        })
        .catch(error => {
            console.error("Error loading page:", error);
        });
}