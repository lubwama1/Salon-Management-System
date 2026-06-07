document.addEventListener("DOMContentLoaded", function () {
  // Image Preview Script
  const imageInput = document.querySelector('input[type="file"]');
  if (imageInput) {
    imageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        // Validate file type
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

        // Validate file size (max 5MB)
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
  // Appointment History - Customer Cancel Modal
  const customCancelAppointmentForm = document.getElementById(
    "customerCancelAppointmentForm",
  );
  const customCancelAppointmentModal = document.getElementById(
    "customerCancelAppointmentModal",
  );
  const serviceNameDisplay = document.getElementById("modal-service-name");
  if (customCancelAppointmentModal) {
    customCancelAppointmentModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      const appointmentId = button.getAttribute("data-appointment-id");
      const serviceName = button.getAttribute("data-service");
      const cancelUrl = button.getAttribute("data-url");
      if (customCancelAppointmentForm && appointmentId) {
        customCancelAppointmentForm.action = cancelUrl;
        customCancelAppointmentForm.method = "POST";
        serviceNameDisplay.textContent = serviceName;
      }
    });
  }

  // Notification Checkbox Handler
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
