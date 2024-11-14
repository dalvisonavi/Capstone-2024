// end_day_report.js

document.addEventListener('DOMContentLoaded', () => {
    let currentPage = 1;
    let rowsPerPage = 10;

    // Sorting Functionality
    function sortTable(columnIndex) {
        const table = document.getElementById("report-table");
        const rows = Array.from(table.rows).slice(1); // Exclude header row
        const isAscending = table.rows[0].cells[columnIndex].classList.toggle("sort-asc");

        // Remove sort-desc class if it was previously applied
        table.rows[0].cells[columnIndex].classList.toggle("sort-desc", !isAscending);

        rows.sort((rowA, rowB) => {
            const cellA = rowA.cells[columnIndex].innerText;
            const cellB = rowB.cells[columnIndex].innerText;

            return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
        });

        rows.forEach(row => table.appendChild(row));
    }

    // Attach click events to header cells for sorting
    const headerCells = document.querySelectorAll("#report-table thead th");
    headerCells.forEach((headerCell, index) => {
        headerCell.addEventListener("click", () => sortTable(index));
    });

    // Filter Functionality
    document.getElementById("searchInput").addEventListener("input", (event) => {
        const filter = event.target.value.toLowerCase();
        const rows = document.getElementById("report-body").rows;

        for (const row of rows) {
            const productName = row.cells[0].textContent.toLowerCase();
            row.style.display = productName.includes(filter) ? "" : "none";
        }
    });

    // Pagination
    function paginateTable() {
        const table = document.getElementById("report-table").getElementsByTagName("tbody")[0];
        const rows = table.getElementsByTagName("tr");

        const totalRows = rows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage);

        for (let i = 0; i < totalRows; i++) {
            rows[i].style.display = i >= (currentPage - 1) * rowsPerPage && i < currentPage * rowsPerPage ? "" : "none";
        }

        document.getElementById("pageNumber").textContent = currentPage;

        document.getElementById("prevPage").disabled = currentPage === 1;
        document.getElementById("nextPage").disabled = currentPage === totalPages;
    }

    // Pagination controls
    document.getElementById("prevPage").addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            paginateTable();
        }
    });

    document.getElementById("nextPage").addEventListener("click", () => {
        currentPage++;
        paginateTable();
    });

    // Initial Pagination Call
    paginateTable();
});
