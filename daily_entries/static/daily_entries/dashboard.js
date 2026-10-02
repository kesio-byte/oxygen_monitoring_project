// dashboard.js

let weeklyChart;

// ---------------- Helpers ----------------
async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }

  return response.json();
}

function setText(element, value) {
  element.textContent = value == null ? "" : String(value);
}

function getEntryTimestamp(entry) {
  const timestamp = new Date(
    `${entry.date ?? ""}T${entry.time ?? "00:00:00"}`
  ).getTime();

  return Number.isNaN(timestamp) ? 0 : timestamp;
}

// ---------------- Alerts ----------------
async function loadAlerts() {
  const alertBox = document.querySelector("#alertsBox");
  if (!alertBox) return;

  try {
    const alerts = await fetchJson("/daily_entries/api/alerts/");
    alertBox.replaceChildren();

    if (!Array.isArray(alerts) || alerts.length === 0) {
      const message = document.createElement("p");
      message.className = "text-gray-500";
      message.textContent = "No alerts at the moment.";
      alertBox.appendChild(message);
      return;
    }

    alerts.forEach(alert => {
      const div = document.createElement("div");

      const levelClass = alert.level === "critical"
        ? "bg-red-100 border-l-4 border-red-500 text-red-700"
        : alert.level === "warning"
        ? "bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700"
        : "bg-green-100 border-l-4 border-green-500 text-green-700";

      div.className = `p-2 mb-2 rounded ${levelClass}`;
      div.textContent = alert.message ?? "";
      alertBox.appendChild(div);
    });
  } catch (error) {
    console.error("Error loading alerts:", error);
  }
}

// ---------------- Live Monitoring ----------------
async function loadLiveData() {
  const box = document.querySelector("#liveBox");
  if (!box) return;

  try {
    const data = await fetchJson("/daily_entries/api/live/");

    if (!data || data.error) {
      const message = document.createElement("p");
      message.className = "text-gray-500";
      message.textContent = "No live data available.";
      box.replaceChildren(message);
      return;
    }

    const purity = Number.parseFloat(data.oxygen_purity);
    const pressure = Number.parseFloat(data.pressure);
    const flowRate = Number.parseFloat(data.flow_rate);
    const pdp = Number.parseFloat(data.pdp);

    const purityClass = Number.isFinite(purity) && purity < 90
      ? "text-red-600 font-bold"
      : "text-green-600";

    const pressureClass = Number.isFinite(pressure) && pressure < 4
      ? "text-orange-600 font-bold"
      : "text-green-600";

    const flowClass = Number.isFinite(flowRate) && flowRate < 3
      ? "text-orange-600 font-bold"
      : "text-green-600";

    const pdpClass = Number.isFinite(pdp) && pdp > -50
      ? "text-red-600 font-bold"
      : "text-green-600";

    const statusClass = data.critical_flag
      ? "bg-red-100 text-red-700"
      : "bg-green-100 text-green-700";

    const statusText = data.critical_flag ? "❌ Critical" : "✅ Normal";

    const wrapper = document.createElement("div");
    wrapper.className = "border border-gray-300 rounded shadow-md";

    const table = document.createElement("table");
    table.className = "table-auto w-full text-sm text-gray-700";

    const tbody = document.createElement("tbody");

    const rows = [
      ["Technician", data.operator],
      ["Date", data.date],
      ["Time", data.time],
      ["Oxygen Purity", `${data.oxygen_purity ?? ""}%`, purityClass],
      ["Pressure", `${data.pressure ?? ""} bar`, pressureClass],
      ["Flow Rate", `${data.flow_rate ?? ""} L/min`, flowClass],
      ["PDP", `${data.pdp ?? ""} °C`, pdpClass],
      ["Status", statusText, `${statusClass} font-bold px-2 py-1 rounded`],
      ["Alert", data.email_sent ? "Email has been sent to the technician" : ""]
    ];

    rows.forEach(([label, value, valueClass = ""]) => {
      const row = document.createElement("tr");

      const heading = document.createElement("th");
      heading.className = "px-4 py-2 text-left";
      heading.textContent = label;

      const cell = document.createElement("td");
      cell.className = `px-4 py-2 ${valueClass}`;
      cell.textContent = value == null ? "" : String(value);

      if (label === "Alert" && data.email_sent) {
        cell.classList.add("text-blue-600", "font-semibold");
      }

      row.append(heading, cell);
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    box.replaceChildren(wrapper);
  } catch (error) {
    console.error("Error loading live data:", error);
  }
}

// ---------------- Entries + Graph ----------------
async function loadEntries() {
  try {
    const entries = await fetchJson("/daily_entries/api/entries/");

    if (!Array.isArray(entries)) {
      throw new Error("The entries API did not return an array.");
    }

    renderTable(entries);

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

// ---------------- Render Table ----------------
function renderTable(entries) {
  const tbody = document.querySelector("#entriesTableBody");
  if (!tbody) return;

  tbody.replaceChildren();

  const newestFirst = [...entries].sort(
    (a, b) => getEntryTimestamp(b) - getEntryTimestamp(a)
  );

  newestFirst.forEach(entry => {
    const row = document.createElement("tr");
    row.className = "hover:bg-gray-50";

    // Keep these columns aligned with your table headings.
    [
      entry.date,
      entry.operator,
      entry.oxygen_purity,
      entry.pressure,
      entry.flow_rate,
      entry.pdp
    ].forEach(value => {
      const cell = document.createElement("td");
      cell.className = "px-4 py-2";
      setText(cell, value);
      row.appendChild(cell);
    });

    tbody.appendChild(row);
  });
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

// ---------------- Initial Load + Polling ----------------
document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  loadEntries();
  loadLiveData();

  setInterval(loadAlerts, 30000);
  setInterval(loadLiveData, 30000);
});