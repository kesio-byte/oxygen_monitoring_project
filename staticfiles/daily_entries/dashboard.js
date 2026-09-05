// ---------------- Live Monitoring ----------------
function loadLiveData() {
  fetch("/daily_entries/api/live/")   // adjust if your route is just "/api/live/"
    .then(res => res.json())
    .then(data => {
      console.log("Fetched live data:", data); // debug
      const box = document.querySelector("#liveBox");
      if (!box) return;

      if (data.error) {
        box.innerHTML = `<p class="text-red-600">${data.error}</p>`;
        return;
      }

      box.innerHTML = `
        <p><strong>Date:</strong> ${data.date} ${data.time}</p>
        <p><strong>Oxygen Purity:</strong> ${data.oxygen_purity}%</p>
        <p><strong>Pressure:</strong> ${data.pressure} bar</p>
        <p><strong>Flow Rate:</strong> ${data.flow_rate} L/min</p>
        <p><strong>PDP:</strong> ${data.pdp} °C</p>
        <p><strong>Status:</strong> ${data.critical_flag ? "❌ Critical — technician emailed" : "✅ Normal"}</p>
      `;

      // Apply background style
      if (data.critical_flag) {
        box.className = "p-6 mb-8 rounded bg-red-100 border-l-4 border-red-500 text-red-700";
      } else {
        box.className = "p-6 mb-8 rounded bg-green-100 border-l-4 border-green-500 text-green-700";
      }
    })
    .catch(err => console.error("Error loading live data:", err));
}
document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000);
  loadEntries();
  loadLiveData();                // <-- must be here
  setInterval(loadLiveData, 5000); // <-- must be here
});
