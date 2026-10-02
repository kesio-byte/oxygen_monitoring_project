// Load live alerts
function loadAlerts() {
  fetch("/daily_entries/api/alerts/?page_unack=1")   // patched
    .then(response => response.json())
    .then(data => {
      const alerts = data.alerts || data; // handle both formats
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
          (alert.critical_flag
            ? "bg-red-100 border-l-4 border-red-500 text-red-700"
            : "bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700");

        div.textContent = `Operator ${alert.operator} at ${alert.time} — Purity ${alert.oxygen_purity}% (Ack: ${alert.technician_ack})`;
        alertBox.appendChild(div);
      });
    })
    .catch(error => {
      console.error("Error loading alerts:", error);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000);
});

// Technician acknowledgment
function updateAck(entryId, checked) {
  const id = parseInt(entryId, 10);

  fetch(`/daily_entries/alerts/ack/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": window.csrfToken,
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest"
    },
    body: new URLSearchParams({ ack: String(checked) })
  })
    .then(response => {
      if (!response.ok) throw new Error(`Request failed: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (!data.success) throw new Error(data.error || "Update failed");

      // Refresh the server-provided count and unacknowledged rows.
      loadUnacknowledged();
    })
    .catch(error => {
      console.error("Error updating technician acknowledgment:", error);
      alert("Failed to update acknowledgment. Please try again.");
      loadUnacknowledged(); // Restore the checkbox/table from server data.
    });
}

// Filter alerts by mode
window.filterAlerts = function(mode) {
  const rows = document.querySelectorAll("tbody tr");
  rows.forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']");
    if (mode === "unack") {
      if (checkbox && !checkbox.checked) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    } else {
      row.style.display = "";
    }
  });
};

// Tab switcher
window.showTab = function(tab) {
  document.getElementById("tab-live").classList.add("hidden");
  document.getElementById("tab-all").classList.add("hidden");
  document.getElementById("tab-unack").classList.add("hidden");

  document.getElementById("tab-" + tab).classList.remove("hidden");

  if (tab === "unack") {
    loadUnacknowledged(1);   // patched
  }
};

// Refresh Unacknowledged tab
function refreshUnack(alerts) {
  const tbody = document.querySelector("#tab-unack tbody");
  tbody.innerHTML = "";

  alerts.forEach(alert => {
    if (!alert.technician_ack) {
      const tr = document.createElement("tr");
      tr.setAttribute("data-entry-id", alert.id);

      tr.innerHTML = `
        <td>${alert.date}</td>
        <td>${alert.time}</td>
        <td>${alert.operator}</td>
        <td>${alert.oxygen_purity}</td>
        <td>${alert.pressure}</td>
        <td>${alert.flow_rate}</td>
        <td>${alert.pdp}</td>
        <td>${alert.notes || "—"}</td>
      `;
      tbody.appendChild(tr);
    }
  });
}

// Load Unacknowledged Alerts
function loadUnacknowledged(page=1) {
  fetch(`/daily_entries/api/alerts/?page_unack=${page}`)   // patched
    .then(res => res.json())
    .then(data => {
      const alerts = data.alerts || data; // handle both formats
      refreshUnack(alerts);

      const badge = document.getElementById("unack-count");
      if (badge) {
        badge.textContent = data.total_unack
          ? data.total_unack.toString()
          : alerts.filter(a => !a.technician_ack).length.toString();
      }
    })
    .catch(err => console.error("Failed to load unacknowledged alerts:", err));
}

document.addEventListener("DOMContentLoaded", () => {
  loadUnacknowledged();
  setInterval(() => loadUnacknowledged(), 30000);
});

// Reload all alerts without wiping ticks
function refreshAll() {
  loadAlerts();
  loadUnacknowledged();
}

fetch("/daily_entries/api/all_alerts/")
  .then(res => res.json())
  .then(alerts => {
    console.log(alerts);
  });
