// dashboard.js

let weeklyChart;

// ---------------- DOM Ready ----------------
document.addEventListener("DOMContentLoaded", () => {
  loadEntries();

  const form = document.querySelector("#entryForm");
  if (form) {
    form.addEventListener("submit", handleEntrySubmit);
  }
});

// ---------------- Submit Entry ----------------
async function handleEntrySubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;

  try {
    const response = await fetch("/add_entry/", {
      method: "POST",
      body: new FormData(form)
    });

    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }

    const data = await response.json();

    if (!data.success) {
      alert("Error: " + JSON.stringify(data.errors ?? "Unable to save entry."));
      return;
    }

    // Reload the table and graph from the server to keep them in sync.
    await loadEntries();
    form.reset();
  } catch (error) {
    console.error("Error submitting entry:", error);
    alert("Could not submit the entry. Please try again.");
  }
}

// ---------------- Fetch Entries ----------------
async function loadEntries() {
  try {
    const response = await fetch("/daily_entries/api/entries/");

    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }

    const entries = await response.json();

    if (!Array.isArray(entries)) {
      throw new Error("The entries API did not return an array.");
    }

    renderTable(entries);

    // Sort a copy chronologically for the graph; don't mutate the original.
    const chronologicalEntries = [...entries].sort(
      (a, b) => getEntryTimestamp(a) - getEntryTimestamp(b)
    );

    renderWeeklyGraph(
      chronologicalEntries.map(entry => entry.date ?? ""),
      chronologicalEntries.map(entry => entry.oxygen_purity ?? null),
      chronologicalEntries.map(entry => entry.pressure ?? null),
      chronologicalEntries.map(entry => entry.flow_rate ?? null),
      chronologicalEntries.map(entry => entry.pdp ?? null)
    );
  } catch (error) {
    console.error("Error loading entries:", error);
  }
}

function getEntryTimestamp(entry) {
  const timestamp = new Date(`${entry.date ?? ""}T${entry.time ?? "00:00:00"}`).getTime();
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

// ---------------- Render Table ----------------
function renderTable(entries) {
  const tbody = document.querySelector("#entriesTableBody");
  if (!tbody) return;

  tbody.replaceChildren();

  const newestFirst = [...entries].sort(
    (a, b) => getEntryTimestamp(b) - getEntryTimestamp(a)
  );

  newestFirst.forEach(entry => {
    tbody.appendChild(createEntryRow(entry));
  });
}

function createEntryRow(entry) {
  const row = document.createElement("tr");
  row.className = "hover:bg-gray-50";

  [
    entry.date,
    entry.time,
    entry.operator,
    entry.oxygen_purity,
    entry.pressure,
    entry.flow_rate,
    entry.pdp
  ].forEach(value => {
    const cell = document.createElement("td");
    cell.className = "px-4 py-2";
    cell.textContent = value == null ? "" : String(value);
    row.appendChild(cell);
  });

  return row;
}

// ---------------- Render / Update Graph ----------------
function renderWeeklyGraph(labels, purityData, pressureData, flowRateData, pdpData) {
  const canvas = document.getElementById("weeklyGraph");
  if (!canvas || typeof Chart === "undefined") return;

  const datasets = [
    { label: "Purity (%)", data: purityData, borderColor: "blue", fill: false },
    { label: "Pressure (bar)", data: pressureData, borderColor: "red", fill: false },
    { label: "Flow Rate (L/min)", data: flowRateData, borderColor: "green", fill: false },
    { label: "PDP (°C)", data: pdpData, borderColor: "orange", fill: false }
  ];

  if (weeklyChart) {
    weeklyChart.data.labels = labels;
    weeklyChart.data.datasets.forEach((dataset, index) => {
      dataset.data = datasets[index].data;
    });
    weeklyChart.update();
    return;
  }

  weeklyChart = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        title: {
          display: true,
          text: "Weekly Oxygen Monitoring Trends"
        }
      }
    }
  });
}

// ---------------- Add a Row ----------------
function addRowToTable(entry) {
  const tbody = document.querySelector("#entriesTableBody");
  if (!tbody) return;

  tbody.prepend(createEntryRow(entry));
}