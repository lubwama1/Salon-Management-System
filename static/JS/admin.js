document.addEventListener("DOMContentLoaded", function () {
  // ========== ENABLE CANCEL BUTTON ==========
  const select = document.getElementById("id_status");
  const btn = document.getElementById("cancel-btn");
  if (select && btn) {
    function toggleButton() {
      btn.disabled = select.value !== "canceled";
    }
    select.addEventListener("change", toggleButton);
    toggleButton();
  }

  // ========== ADMIN IMAGE PREVIEW ==========
  const adminImageInput = document.querySelector("#admin_image_input");
  if (adminImageInput) {
    adminImageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const preview = document.getElementById("adminImagePreview");
          if (preview) {
            preview.src = event.target.result;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ========== CUSTOMER IMAGE PREVIEW ==========
  const customerImageInput = document.querySelector("#customer_image_input");
  if (customerImageInput) {
    customerImageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const validTypes = [
          "image/jpeg",
          "image/png",
          "image/jpg",
          "image/gif",
        ];
        if (!validTypes.includes(file.type)) {
          alert("Please upload a valid image file (JPEG, PNG, or GIF)");
          this.value = "";
          return;
        }
        if (file.size > 5 * 1024 * 1024) {
          alert("File size must be less than 5MB");
          this.value = "";
          return;
        }
        const reader = new FileReader();
        reader.onload = function (event) {
          const preview = document.getElementById("customerImagePreview");
          if (preview) {
            preview.src = event.target.result;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ========== APPROVAL FORM (Reviews Page) ==========
  const approvalForms = document.querySelectorAll(".approval-form");
  if (approvalForms.length > 0) {
    approvalForms.forEach((form) => {
      const csrfTokenElem = form.querySelector("[name=csrfmiddlewaretoken]");
      const checkbox = form.querySelector(".approval-checkbox");

      if (!csrfTokenElem || !checkbox) return;

      const csrfToken = csrfTokenElem.value;
      const url = form.action;
      let originalState = checkbox.checked;

      checkbox.addEventListener("change", function () {
        const isChecked = this.checked;
        const badgeSpan = form.querySelector(".badge");
        this.disabled = true;

        fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ approved: isChecked }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              if (badgeSpan) {
                if (isChecked) {
                  badgeSpan.innerHTML = "Approved";
                  badgeSpan.className = "badge bg-success rounded-pill";
                } else {
                  badgeSpan.innerHTML = "Pending";
                  badgeSpan.className =
                    "badge bg-warning text-dark rounded-pill";
                }
              }
              originalState = isChecked;
            } else {
              checkbox.checked = originalState;
              alert(data.message || "Error updating review");
              if (badgeSpan) {
                badgeSpan.innerHTML = originalState ? "Approved" : "Pending";
                badgeSpan.className = originalState
                  ? "badge bg-success rounded-pill"
                  : "badge bg-warning text-dark rounded-pill";
              }
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            checkbox.checked = originalState;
            alert("Network error. Please try again.");
          })
          .finally(() => {
            checkbox.disabled = false;
          });
      });
    });
  }

  // ========== COMMENT MODAL ==========
  const commentModal = document.getElementById("commentModal");
  if (commentModal) {
    commentModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const commentText = button.getAttribute("data-comment");
      const modalComment = document.getElementById("modalCommentText");
      if (modalComment && commentText) {
        modalComment.innerHTML = `"${commentText}"`;
      } else if (modalComment) {
        modalComment.innerHTML = "No comment provided.";
      }
    });
  }

  // ========== VIEW REVIEW MODAL (Combined Desktop & Mobile) ==========
  function setupReviewModal(selector) {
    const viewReviewBtns = document.querySelectorAll(selector);
    viewReviewBtns.forEach((btn) => {
      btn.addEventListener("click", function () {
        const viewCustomer = document.getElementById("viewCustomer");
        const viewService = document.getElementById("viewService");
        const viewComment = document.getElementById("viewComment");
        const viewDate = document.getElementById("viewDate");
        const viewRating = document.getElementById("viewRating");

        if (viewCustomer) viewCustomer.innerText = this.dataset.customer || "-";
        if (viewService) viewService.innerText = this.dataset.service || "-";
        if (viewComment)
          viewComment.innerText =
            this.dataset.comment || "No comment provided.";
        if (viewDate) viewDate.innerText = this.dataset.date || "-";

        if (viewRating) {
          const rating = parseInt(this.dataset.rating) || 0;
          let starsHtml = "";
          for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
              starsHtml += '<i class="fas fa-star text-warning me-1"></i>';
            } else {
              starsHtml += '<i class="far fa-star text-secondary me-1"></i>';
            }
          }
          starsHtml += `<span class="ms-2 small text-muted">(${rating}/5)</span>`;
          viewRating.innerHTML = starsHtml;
        }
      });
    });
  }

  setupReviewModal(".view-review-btn");
  setupReviewModal(".view-review-btn-mobile");

  // ========== DELETE REVIEW MODAL (Combined Desktop & Mobile) ==========
  const deleteReviewForm = document.getElementById("deleteReviewForm");
  const deleteReviewModal = document.getElementById("deleteReviewModal");

  if (deleteReviewModal) {
    deleteReviewModal.addEventListener("show.bs.modal", (event) => {
      const btn = event.relatedTarget;
      if (!btn) return;

      const reviewId = btn.getAttribute("data-review-id");
      const reviewUrl = btn.getAttribute("data-url");

      if (deleteReviewForm && reviewUrl) {
        deleteReviewForm.action = reviewUrl;
      }

      const deleteReviewId = document.getElementById("deleteReviewId");
      if (deleteReviewId && reviewId) {
        deleteReviewId.value = reviewId;
      }
    });
  }

  // ========== DELETE CATEGORY MODAL ==========
  const deleteCategoryForm = document.getElementById("deleteCategoryForm");
  const deleteCategoryModal = document.getElementById("DeleteCategoryModal");
  const categoryNameDisplay = document.getElementById("categoryNameDisplay");

  if (deleteCategoryModal) {
    deleteCategoryModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const categoryId = button.getAttribute("data-category-id");
      const categoryName = button.getAttribute("data-category-name");
      const categoryUrl = button.getAttribute("data-url");

      if (categoryNameDisplay && categoryName) {
        categoryNameDisplay.innerText = categoryName;
      }

      if (deleteCategoryForm && categoryUrl) {
        deleteCategoryForm.action = categoryUrl;
        deleteCategoryForm.method = "POST";
      }
    });
  }

  // ========== DELETE CUSTOMER MODAL ==========
  const deleteCustomerForm = document.getElementById("deleteCustomerForm");
  const customerNameDisplay = document.getElementById("customerNameDisplay");
  const deleteCustomerModal = document.getElementById("DeleteCustomerModal");

  if (deleteCustomerModal) {
    deleteCustomerModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const customerUrl = button.getAttribute("data-url");
      const customerName = button.getAttribute("data-customer-name");

      if (deleteCustomerForm && customerUrl) {
        deleteCustomerForm.action = customerUrl;
      }
      if (customerNameDisplay && customerName) {
        customerNameDisplay.innerText = customerName;
      }
    });
  }

  // ========== DELETE STAFF MODAL ==========
  const deleteStaffForm = document.getElementById("deleteStaffForm");
  const staffNameDisplay = document.getElementById("staffNameDisplay");
  const deleteStaffModal = document.getElementById("DeleteStaffModal");

  if (deleteStaffModal) {
    deleteStaffModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const staffUrl = button.getAttribute("data-url");
      const staffName = button.getAttribute("data-staff-name");

      if (deleteStaffForm && staffUrl) {
        deleteStaffForm.action = staffUrl;
      }
      if (staffNameDisplay && staffName) {
        staffNameDisplay.innerText = staffName;
      }
    });
  }

  // ========== DELETE SERVICE MODAL ==========
  const deleteServiceForm = document.getElementById("deleteServiceForm");
  const deleteServiceModal = document.getElementById("DeleteServiceModal");
  const serviceNameDisplay = document.getElementById("serviceNameDisplay");

  if (deleteServiceModal) {
    deleteServiceModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const serviceUrl = button.getAttribute("data-url");
      const serviceName = button.getAttribute("data-service-name");

      if (deleteServiceForm && serviceUrl) {
        deleteServiceForm.action = serviceUrl;
      }
      if (serviceNameDisplay && serviceName) {
        serviceNameDisplay.innerText = serviceName;
      }
    });
  }

  // ========== CANCEL APPOINTMENT MODAL ==========
  const appointmentCancelForm = document.getElementById(
    "cancelAppointmentForm",
  );
  const appointmentCancelModal = document.getElementById(
    "CancelAppointmentModal",
  );

  if (appointmentCancelModal) {
    appointmentCancelModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const actionUrl = button.getAttribute("data-url");
      if (appointmentCancelForm && actionUrl) {
        appointmentCancelForm.action = actionUrl;
      }
    });
  }

  // ========== EXPERIENCE DURATION ==========
  const experienceDurationElement = document.getElementById(
    "experience-duration",
  );
  if (experienceDurationElement) {
    const startYear = 2023;
    const currentYear = new Date().getFullYear();
    const experienceDuration = currentYear - startYear;
    experienceDurationElement.innerText = experienceDuration;
  }

  // ========== FILTER STAFF DATA ==========
  const staffSearch = document.getElementById("staffSearch");
  if (staffSearch) {
    let timer;
    staffSearch.addEventListener("keyup", function () {
      clearTimeout(timer);
      let query = this.value;
      timer = setTimeout(() => {
        fetch(`/staff/search?q=${query}`)
          .then((response) => response.json())
          .then((data) => {
            let rows = "";
            const staffTableBody = document.getElementById("staffTableBody");
            if (staffTableBody) {
              data.staff.forEach((staff, index) => {
                rows += `
                  <tr>
                    <td>${index + 1}</td>
                    <td class="fw-semibold text-primary">${staff.user__username}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td><span class="badge bg-primary text-white">${staff.employee_number}</span></td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td><a href="/staff/${staff.id}/" class="btn btn-sm btn-outline-primary"><i class="fas fa-eye"></i></a></td>
                  </tr>
                `;
              });
              staffTableBody.innerHTML = rows;
            }
          })
          .catch((error) => console.error("Error searching staff:", error));
      }, 300);
    });
  }

  // ========== NOTIFICATION CHECKBOX HANDLER ==========
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
