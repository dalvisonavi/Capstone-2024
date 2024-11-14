// script.js
document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('form button[type="submit"]');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmDelete = confirm("Are you sure you want to delete this item?");
            if (!confirmDelete) {
                event.preventDefault(); // Prevent form submission
            }
        });
    });
});
