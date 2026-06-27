<<<<<<< HEAD
=======
// dashboard.js

let weeklyChart; // keep reference so we can update instead of recreate

document.addEventListener("DOMContentLoaded", () => {
  loadEntries(); // initial load

  // Attach AJAX submission to entry form
  const form = document.querySelector("#entryForm");
  if (form) {
    form.addEventListener("submit", e => {
      e.preventDefault();
      fetch("/add_entry/", {
        method: "POST",
        body: new FormData(form)
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          addRowToTable(data.entry);
          updateGraph(); // reload graph data
          form.reset();
        } else {
          alert("Error: " + JSON.stringify(data.errors));
        }
      });
    });
  }
});

// Fetch entries JSON and render table + graph
// Fetch entries JSON and render table + graph
function loadEntries() {
  fetch("/daily_entries/api/entries/")   // 👈 corrected path
    .then(res => res.json())
    .then(entries => {
      console.log("Fetched entries:", entries); // debug
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

// Render table dynamically
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

// Updated renderWeeklyGraph with persistent chart
>>>>>>> 39c4455 (Implement three-stage alerts model and dashboard integration)
function renderWeeklyGraph(labels, purityData, pressureData, flowRateData, pdpData) {
  const ctx = document.getElementById('weeklyGraph').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: 'Purity (%)', data: purityData, borderColor: 'blue', fill: false },
        { label: 'Pressure (bar)', data: pressureData, borderColor: 'red', fill: false },
        { label: 'Flow Rate (L/min)', data: flowRateData, borderColor: 'green', fill: false },
        { label: 'PDP (dB)', data: pdpData, borderColor: 'orange', fill: false }
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
