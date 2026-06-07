// document.addEventListener("DOMContentLoaded", function () {
//   const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
//   const userIdElement = document.getElementById("user-id");

//   if (userIdElement) {
//     const userId = userIdElement.value;
//     const url = `${protocol}//${window.location.host}/ws/notifications/${userId}/`;

//     if (userId) {
//       const socket = new WebSocket(url);

//       socket.onopen = function () {
//         console.log("WebSocket connection established for notifications");
//         loadNotifications();
//       };

//       socket.onmessage = function (e) {
//         const data = JSON.parse(e.data);
//         console.log("Received notification:", data);
//         // showNotificationToast(data);
//         loadNotifications();
//       };

//       socket.onclose = function (e) {
//         console.log("WebSocket connection closed for notifications");
//       };

//       socket.onerror = function (e) {
//         console.error("WebSocket error for notifications:", e);
//       };
//     }
//   }
//   function loadNotifications() {
//     fetch("/notifications/list/")
//       .then((response) => response.json())
//       .then((data) => {
//         const notificationCount = document.getElementById("notification-count");
//         if (notificationCount && data) {
//           notificationCount.textContent = data.unread_count || 0;
//         }
//       })
//       .catch((error) => console.error("Error loading notifications:", error));
//   }

//   loadNotifications();
//   setInterval(loadNotifications, 5000);
// });
