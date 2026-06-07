document.addEventListener("DOMContentLoaded", function () {
  // Image Preview Script
  const imageInput = document.querySelector('input[type="file"]');
  if (imageInput) {
    imageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const preview = document.getElementById("staffImagePreview");
          if (preview) {
            preview.src = event.target.result;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Status Filter Functionality
  const statusFilter = document.getElementById("statusFilter");
  const tbody = document.getElementById("tableBody");

  function filterRows() {
    if (!tbody) return;

    const selectedStatus = statusFilter ? statusFilter.value : "all";
    const rows = document.querySelectorAll("#tableBody tr");
    let visibleCount = 0;

    rows.forEach((row) => {
      // Skip the no result row if it exists
      if (row.id === "noResultRow") return;

      let show = true;
      if (selectedStatus !== "all") {
        const rowStatus = row.getAttribute("data-status");
        if (rowStatus !== selectedStatus) show = false;
      }

      row.style.display = show ? "" : "none";
      if (show) visibleCount++;
    });

    // Show/hide no results message
    const noResultRow = document.getElementById("noResultRow");
    if (visibleCount === 0 && rows.length > 0) {
      if (!noResultRow && tbody) {
        const newRow = document.createElement("tr");
        newRow.id = "noResultRow";
        const colspan = document.querySelector("#tableBody tr:first-child td")
          ? document.querySelector("#tableBody tr:first-child td").colSpan
          : 5;
        newRow.innerHTML = `<td colspan="${colspan}" class="text-center text-muted py-4">
          <i class="fas fa-search me-1"></i> No matching appointments found.
        </td>`;
        tbody.appendChild(newRow);
      }
    } else if (noResultRow) {
      noResultRow.remove();
    }
  }

  // Add event listener for status filter
  if (statusFilter) {
    statusFilter.addEventListener("change", filterRows);
  }

  // Desktop View Modal Handler
  const viewButtons = document.querySelectorAll(".view-details");
  viewButtons.forEach((button) => {
    button.addEventListener("click", function () {
      document.getElementById("modalCustomer").textContent =
        this.dataset.customer || "-";
      document.getElementById("modalService").textContent =
        this.dataset.service || "-";
      document.getElementById("modalDate").textContent =
        this.dataset.date || "-";
      document.getElementById("modalTime").textContent =
        this.dataset.time || "-";
      document.getElementById("modalStatus").innerHTML =
        `<span class="badge bg-primary">${this.dataset.statusDisplay || "-"}</span>`;
    });
  });

  // Mobile View Modal Handler
  const mobileViewButtons = document.querySelectorAll(".view-details-mobile");
  mobileViewButtons.forEach((button) => {
    button.addEventListener("click", function () {
      document.getElementById("modalCustomer").textContent =
        this.dataset.customer || "-";
      document.getElementById("modalService").textContent =
        this.dataset.service || "-";
      document.getElementById("modalDate").textContent =
        this.dataset.date || "-";
      document.getElementById("modalTime").textContent =
        this.dataset.time || "-";
      document.getElementById("modalStatus").innerHTML =
        `<span class="badge bg-primary">${this.dataset.statusDisplay || "-"}</span>`;
    });
  });

  // Notification Checkbox Handler (Select All)
  const selectAll = document.getElementById("select-all");
  if (selectAll) {
    selectAll.addEventListener("change", function () {
      const checkBoxes = document.querySelectorAll(".notification-checkbox");
      checkBoxes.forEach((checkbox) => {
        checkbox.checked = this.checked;
      });
    });
  }
});
