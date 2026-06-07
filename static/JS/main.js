document.addEventListener("DOMContentLoaded", function () {
  let currentSelectedId = null;
  let currentSelectedStaff = null;
  const staffBtn = document.querySelectorAll(".select-staff-btn");
  const staffNameDisplay = document.getElementById("selectedStaffDisplay");
  const selectedStaffInput = document.getElementById("selectedStaffInput");
  const form = document.getElementById("appointmentReviewForm");
  const submitBtn = document.getElementById("submitBtn");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.5";
    submitBtn.style.cursor = "not-allowed";
    submitBtn.title = "Please select a staff member before submitting.";
  }
  function updatedSelectedStaff(staffId, staffName) {
    currentSelectedId = staffId;
    currentSelectedStaff = staffName;
    if (currentSelectedId && currentSelectedStaff) {
      staffNameDisplay.innerText = `Selected Staff: ${staffName}`;
      staffNameDisplay.classList.remove("text-muted", "fw-normal");
      staffNameDisplay.classList.add("text-success", "fw-bold");
      selectedStaffInput.value = staffId;
    }
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.style.cursor = "pointer";
      submitBtn.title = "Submit your decision";
    }
    // Clear any validation errors
    const alertInfo = document.querySelector(".alert-info");
    if (alertInfo) {
      alertInfo.classList.remove("border", "border-danger");
    }

    // Remove any existing error messages
    const existingError = document.querySelector(".staff-required-error");
    if (existingError) existingError.remove();
    document.querySelectorAll("#staffTableBody tr").forEach((row) => {
      const btn = row.querySelector(".select-staff-btn");
      if (btn && btn.getAttribute("data-staff-id") == staffId) {
        row.classList.add("table-active");
        const chooseBtn = row.querySelector(".btn-outline-success");
        if (chooseBtn) {
          chooseBtn.classList.remove("btn-outline-success");
          chooseBtn.classList.add("btn-success", "text-white");
          chooseBtn.innerHTML = '<i class="fas fa-check me-1"></i> Assigned';
        }
      } else {
        row.classList.remove("table-active");
        const otherBtn = row.querySelector(".btn");
        if (otherBtn && otherBtn.innerText.includes("Assigned")) {
          otherBtn.classList.remove("btn-success", "text-white");
          otherBtn.classList.add("btn-outline-success");
          otherBtn.innerHTML = '<i class="fas fa-user-check me-1"></i> Choose';
        } else if (otherBtn && !otherBtn.innerText.includes("Assigned")) {
          if (!otherBtn.classList.contains("btn-outline-success")) {
            otherBtn.classList.add("btn-outline-success");
            otherBtn.classList.remove("btn-success");
          }
        }
      }
    });
  }

  //  Scroll animation for about page
  const scrollElements = document.querySelectorAll(
    ".offer-scroll, .team-scroll",
  );

  // Set initial hidden state
  scrollElements.forEach((elem) => {
    elem.style.opacity = "0";
    elem.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)";

    if (elem.classList.contains("offer-scroll")) {
      elem.style.transform = "scale(0.8)";
    } else {
      elem.style.transform = "translateY(30px)";
    }
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const element = entry.target;

          // Apply different delays based on position
          const delay = element.dataset.delay || "0s";
          element.style.transitionDelay = delay;

          // Reveal the element
          element.style.opacity = "1";

          if (element.classList.contains("offer-scroll")) {
            element.style.transform = "scale(1)";
          } else {
            element.style.transform = "translateY(0)";
          }

          // Optional: Add Animate.css class after reveal
          const animation = element.dataset.animation;
          if (animation) {
            setTimeout(() => {
              element.classList.add(
                "animate__animated",
                `animate__${animation}`,
              );
            }, 100);
          }

          observer.unobserve(element);
        }
      });
    },
    { threshold: 0.2 },
  );

  scrollElements.forEach((element) => observer.observe(element));

  // const changeStaffBtn = document.getElementById("ChangeStaff");
  // const staffTable = document.getElementById("StaffTable");

  // changeStaffBtn.addEventListener("click", function () {
  //   staffTable.classList.toggle("d-none");
  // });

  // Privacy Last Updated Date
  const lastUpdatedElem = document.getElementById("last-updated");
  if (lastUpdatedElem) {
    const lastUpdatedDate = new Date(document.lastModified);
    const options = { year: "numeric", month: "long", day: "numeric" };
    lastUpdatedElem.textContent = lastUpdatedDate.toLocaleDateString(
      undefined,
      options,
    );
  }
  // Accodion smooth scroll
  const accordionButtons = document.querySelectorAll(".accordion-button");
  accordionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const expand =
        this.getAttribute("aria-expanded") === "true" ? false : true;
      this.setAttribute("aria-expanded", expand);
    });
  });
  staffBtn.forEach((btn) => {
    btn.addEventListener("click", function () {
      const staffId = this.getAttribute("data-staff-id");
      const staffName = this.getAttribute("data-staff-name");
      updatedSelectedStaff(staffId, staffName);

      const alertDiv = document.createElement("div");
      alertDiv.className =
        "alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3 shadow rounded-pill";
      alertDiv.style.zIndex = "9999";
      alertDiv.style.maxWidth = "350px";
      alertDiv.innerHTML = `<i class="fas fa-user-check me-2"></i> Staff "${staffName}" assigned. <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>`;
      document.body.appendChild(alertDiv);

      setTimeout(() => {
        alertDiv.classList.remove("show");
        setTimeout(() => alertDiv.remove(), 300);
      }, 2000);
    });
  });

  setTimeout(() => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 3000);

  const currentYear = document.getElementById("current-year");
  if (currentYear) {
    currentYear.textContent = new Date().getFullYear();
  }

  (function () {
    const statusFilter = document.getElementById("statusFilter");
    const rows = document.querySelectorAll("#tableBody tr");
    const tableBody = document.getElementById("tableBody");
    const searchFilter = document.getElementById("searchFilter");
    function filterRows() {
      const status = statusFilter ? statusFilter.value : "all";
      const query = searchFilter ? searchFilter.value.toLowerCase() : "";
      rows.forEach((row) => {
        let show = true;
        if (status != "all") {
          const rowStatus = row.getAttribute("data-status");
          if (rowStatus != status) show = false;
        }

        if (query && show) {
          const name = row.getAttribute("data-name") || "";
          const email = row.getAttribute("data-email") || "";
          if (!name.includes(query) && !email.includes(query)) show = false;
        }

        row.style.display = show ? "" : "none";
      });
      if (statusFilter) statusFilter.addEventListener("change", filterRows);
      if (searchFilter) searchFilter.addEventListener("keyup", filterRows);
    }
    filterRows();
  })();

  // Site logo handler

  const siteLogoInput = document.querySelector('input[type="file"]');
  if (siteLogoInput) {
    siteLogoInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const preview = document.getElementById("siteLogoPreview");
          if (preview) {
            preview.src = event.target.result;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Site Form Submission Spinner

  // const settingsForm = document.getElementById("siteSettingForm");
  // if (settingsForm) {
  //   settingsForm.addEventListener("submit", function () {
  //     const btn = settingsForm.querySelector("button[type='submit']");
  //     if (btn) {
  //       btn.disabled = true;
  //       btn.innerHTML =
  //         '<i class="fas fa-spinner fa-spin me-1"></i>Updating...';
  //     }
  //   });
  // }

  const settingsForm = document.getElementById("siteSettingForm");
  if (settingsForm) {
    settingsForm.addEventListener("submit", function () {
      const submitBtn = settingsForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        // Store original content
        const originalText = submitBtn.innerHTML;
        const originalClass = submitBtn.className;

        // Disable and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML =
          '<i class="fas fa-spinner fa-spin me-2"></i> Updating...';

        // Optional: Add a timeout to reset if submission takes too long
        setTimeout(function () {
          if (submitBtn.disabled) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            submitBtn.className = originalClass;
          }
        }, 15000); // Reset after 15 seconds
      }
    });
  }
});
