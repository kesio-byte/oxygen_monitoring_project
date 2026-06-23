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
