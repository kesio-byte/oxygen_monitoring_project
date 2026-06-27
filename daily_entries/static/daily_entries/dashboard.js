function loadAlerts() {
  fetch("/daily_entries/api/alerts/")
    .then(res => res.json())
    .then(alerts => {
      console.log("Fetched alerts:", alerts); // 👈 debug
      const alertBox = document.querySelector("#alertsBox");
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

document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  setInterval(loadAlerts, 30000); // refresh every 30s
});



