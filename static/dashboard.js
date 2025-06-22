// Fetch summary counts and inject into the cards
async function loadSummary() {
  const resp = await fetch('/api/dashboard/summary');
  const { smsSent, simActive, tasksPending } = await resp.json();
  document.getElementById('sms-sent-count').textContent   = smsSent;
  document.getElementById('sim-active-count').textContent = simActive;
  document.getElementById('tasks-count').textContent      = tasksPending;
}

// Fetch chart data and render two Chart.js charts
async function loadCharts() {
  const resp = await fetch('/api/dashboard/charts');
  const { signalHistory, smsVolume } = await resp.json();

  // signalHistory: { labels: [...timestamps], data: [...averages] }
  new Chart(document.getElementById('signalChart'), {
    type: 'line',
    data: {
      labels: signalHistory.labels,
      datasets: [{
        label: 'Qualité moyenne',
        data: signalHistory.data,
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      scales: { y: { beginAtZero: true, max: 31 } }
    }
  });

  // smsVolume: { labels: [...hours], data: [...counts] }
  new Chart(document.getElementById('smsVolumeChart'), {
    type: 'bar',
    data: {
      labels: smsVolume.labels,
      datasets: [{
        label: 'SMS envoyés',
        data: smsVolume.data
      }]
    },
    options: {
      scales: { y: { beginAtZero: true } }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadSummary();
  loadCharts();
});

