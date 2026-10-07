// Load the latest system alert messages.
function loadAlerts() {
  fetch("/daily_entries/api/alerts/?page_unack=1")
    .then(response => {
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const alertBox = document.getElementById("alertsBox");
      if (!alertBox) return;

      alertBox.innerHTML = "";
      const alerts = data.alerts || [];

      if (alerts.length === 0) {
        alertBox.innerHTML =
          "<p class='text-gray-500'>No alerts at the moment.</p>";
        return;
      }

      alerts.forEach(alert => {
        const div = document.createElement("div");
        div.className =
          "p-2 mb-2 rounded " +
          (alert.type === "critical"
            ? "bg-red-100 border-l-4 border-red-500 text-red-700"
            : "bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700");

        div.textContent = alert.message || "System alert";
        alertBox.appendChild(div);
      });
    })
    .catch(error => console.error("Error loading alerts:", error));
}

//-- Update an alert's acknowledgment status.--
function updateAck(entryId, checked) {
  const id = parseInt(entryId, 10);
  if (!Number.isInteger(id)) {
    console.error("Invalid alert entry ID:", entryId);
    return;
  }
  
  //-- Send a POST request to update the acknowledgment status. ---
  fetch(`/daily_entries/alerts/ack/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": window.csrfToken || "",
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest"
    },
    body: new URLSearchParams({ ack: String(checked) })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.error || "Acknowledgment update failed");
      }

      // Keep the matching checkbox in All Alerts in sync.
      document
        .querySelectorAll(
          `#tab-all input[aria-label="Acknowledge ${id}"]`
        )
        .forEach(checkbox => {
          checkbox.checked = data.ack;
        });

      loadUnacknowledged();
    })
    .catch(error => {

      //-- Log the error and alert the user. ---
      console.error("Error updating acknowledgment:", error);
      alert("Failed to update acknowledgment. Please try again.");
      loadUnacknowledged();
    });
}

//-- Filter table rows by acknowledgment status.--
window.filterAlerts = function (mode) {
  document.querySelectorAll("tbody tr").forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']");

    if (mode === "unack") {
      row.style.display = checkbox && !checkbox.checked ? "" : "none";
    } else {
      row.style.display = "";
    }
  });
};

//-- Switch tabs.--
window.showTab = function (tab) {
  ["live", "all", "unack"].forEach(name => {
    const element = document.getElementById(`tab-${name}`);
    if (element) element.classList.add("hidden");
  });

  const selectedTab = document.getElementById(`tab-${tab}`);
  if (selectedTab) selectedTab.classList.remove("hidden");

  if (tab === "unack") {
    loadUnacknowledged(1);
  }
};

//-- Render unacknowledged entry records.--
function refreshUnack(entries) {
  const tbody = document.querySelector("#tab-unack tbody");
  if (!tbody) return;

  tbody.innerHTML = "";

 //-- If there are no unacknowledged entries, show a message. --
  if (!entries.length) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td colspan="9" class="px-4 py-10 text-center text-sm text-gray-500">
        No unacknowledged alerts.
      </td>
    `;
    tbody.appendChild(row);
    return;
  }

  entries.forEach(entry => {
    const row = document.createElement("tr");
    row.dataset.entryId = entry.id;
    row.className = "hover:bg-gray-50 transition-colors";
 
    const values = [
      entry.date,
      entry.time,
      entry.operator,
      entry.oxygen_purity,
      entry.pressure,
      entry.flow_rate,
      entry.pdp,
      entry.notes || "—"
    ];
   
    values.forEach((value, index) => {
      const cell = document.createElement("td");
      cell.textContent = value ?? "—";
      cell.className = "px-4 py-3 text-gray-700";
     
      //-- Apply specific styles based on the column index. --
      if (index === 0 || index === 1) {
        cell.classList.add("whitespace-nowrap");
      }
      if (index >= 3 && index <= 6) {
        cell.classList.add("whitespace-nowrap", "text-right", "font-mono", "tabular-nums");
      }
      if (index === 7) {
        cell.classList.add("truncate");
        cell.title = value || "—";
      }

      row.appendChild(cell);
    });

    const ackCell = document.createElement("td");
    ackCell.className = "px-4 py-3 text-center";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className =
      "h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer";
    checkbox.checked = Boolean(entry.technician_ack);
    checkbox.setAttribute("aria-label", `Acknowledge alert ${entry.id}`);
    checkbox.addEventListener("change", () =>
      updateAck(entry.id, checkbox.checked)
    );

    ackCell.appendChild(checkbox);
    row.appendChild(ackCell);
    tbody.appendChild(row);
  });
}

//-- Load unacknowledged entry records.--
function loadUnacknowledged(page = 1) {

  //-- Fetch unacknowledged entries from the API BOX.--
  fetch(`/daily_entries/api/alerts/?page_unack=${page}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const entries = data.entries || [];
      refreshUnack(entries);

      const badge = document.getElementById("unack-count");
      if (badge) {
        badge.textContent = String(data.total_unack ?? entries.length);
      }
    })
    .catch(error =>
      console.error("Failed to load unacknowledged alerts:", error)
    );
}

//-- Refresh both alert sections.--
function refreshAll() {
  loadAlerts();
  loadUnacknowledged();
}

//-- Initialize the alert system when the DOM is fully loaded.--
document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  loadUnacknowledged();

  setInterval(loadAlerts, 30000);
  setInterval(loadUnacknowledged, 30000);
});