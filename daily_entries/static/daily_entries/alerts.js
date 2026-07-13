// alerts.js

function loadAlerts() {
  fetch("/daily_entries/api/alerts/")   // ✅ must match urls.py
    .then(res => res.json())
    .then(alerts => {
      console.log("Fetched alerts:", alerts); // debug
      const alertBox = document.querySelector("#alertsBox");
      if (!alertBox) return;
      alertBox.innerHTML = "";
      alerts.forEach(a => {
        const div = document.createElement("div");
        div.className = "p-2 mb-2 rounded " +
          (a.level === "critical" ? "bg-red-100 border-l-4 border-red-500 text-red-700" :
           a.level === "warning" ? "bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700" :
           "bg-green-100 border-l-4 border-green-500 text-green-700");
        div.textContent = a.message;
        alertBox.appendChild(div);
      });
    })
    .catch(err => {
      const box = document.getElementById("alertsBox");
      if (box) {
        box.innerHTML = "<p class='text-red-500'>Error loading alerts</p>";
      }
      console.error("Error fetching alerts:", err);
    });
}

// Auto-refresh every 30s
document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000);
});
