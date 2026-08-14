// Load live alerts
function loadAlerts() {
  fetch("/daily_entries/api/alerts/")
    .then(response => response.json())
    .then(alerts => {
      const alertBox = document.getElementById("alertsBox");
      alertBox.innerHTML = "";

      if (!alerts || alerts.length === 0) {
        alertBox.innerHTML = "<p class='text-gray-500'>No alerts at the moment.</p>";
        return;
      }

      alerts.forEach(alert => {
        const div = document.createElement("div");
        div.className =
          "p-2 mb-2 rounded " +
          (alert.level === "critical"
            ? "bg-red-100 border-l-4 border-red-500 text-red-700"
            : alert.level === "warning"
            ? "bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700"
            : "bg-green-100 border-l-4 border-green-500 text-green-700");

        div.textContent = alert.message;
        alertBox.appendChild(div);
      });
    })
    .catch(error => {
      console.error("Error loading alerts:", error);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000); // refresh every 30s
});

// Technician acknowledgment
function updateAck(entryId, checked) {
  const id = parseInt(entryId, 10); // ensure numeric
  fetch(`/daily_entries/alerts/ack/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": window.csrfToken,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: "ack=" + checked
  })
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        alert("Failed to update technician acknowledgment");
      }
    })
    .catch(err => {
      console.error("Error updating technician ack:", err);
    });
}

// Filter alerts by mode
window.filterAlerts = function(mode) {
  const rows = document.querySelectorAll("tbody tr");
  rows.forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']");
    if (mode === "unack") {
      // Show only rows with unchecked boxes
      if (checkbox && !checkbox.checked) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    } else {
      // Show all rows
      row.style.display = "";
    }
  });
};
