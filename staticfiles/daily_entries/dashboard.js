// dashboard.js

let weeklyChart; // keep reference so we can update instead of recreate

// ---------------- Alerts ----------------
function loadAlerts() {
  fetch("/daily_entries/api/alerts/")
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
    .catch(err => console.error("Error loading alerts:", err));
}

// ---------------- Entries + Graph ----------------
function loadEntries() {
  fetch("/daily_entries/api/entries/")
    .then(res => res.json())
    .then(entries => {
      console.log("Fetched entries:", entries);
      renderTable(entries);
      renderWeeklyGraph(
        entries.map(e => e.date).reverse(),
        entries.map(e => e.oxygen_purity).reverse(),
        entries.map(e => e.pressure).reverse(),
        entries.map(e => e.flow_rate).reverse(),
        entries.map(e => e.pdp).reverse()
      );
    })
    .catch(err => console.error("Error loading entries:", err));
}

function renderTable(entries) {
  const tbody = document.querySelector("#entriesTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";
  entries.forEach(e => {
    const row = document.createElement("tr");
    row.className = "hover:bg-gray-50";
    row.innerHTML = `
      <td class="px-4 py-2">${e.date}</td>
      <td class="px-4 py-2">${e.operator}</td>
      <td class="px-4 py-2">${e.oxygen_purity}</td>
      <td class="px-4 py-2">${e.pressure}</td>
      <td class="px-4 py-2">${e.flow_rate}</td>
      <td class="px-4 py-2">${e.pdp}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderWeeklyGraph(labels, purityData, pressureData, flowRateData, pdpData) {
  const canvas = document.getElementById('weeklyGraph');
  if (!canvas) return; // avoid null error
  const ctx = canvas.getContext('2d');
  if (weeklyChart) {
    weeklyChart.data.labels = labels;
    weeklyChart.data.datasets[0].data = purityData;
    weeklyChart.data.datasets[1].data = pressureData;
    weeklyChart.data.datasets[2].data = flowRateData;
    weeklyChart.data.datasets[3].data = pdpData;
    weeklyChart.update();
  } else {
    weeklyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'Purity (%)', data: purityData, borderColor: 'blue', fill: false },
          { label: 'Pressure (bar)', data: pressureData, borderColor: 'red', fill: false },
          { label: 'Flow Rate (L/min)', data: flowRateData, borderColor: 'green', fill: false },
          { label: 'PDP (°C)', data: pdpData, borderColor: 'orange', fill: false }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: true, text: 'Weekly Oxygen Monitoring Trends' }
        }
      }
    });
  }
}

// ---------------- DOM Ready ----------------
document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000); // refresh alerts every 30s
  loadEntries();
});
