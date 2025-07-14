// static/ussd.js

document.addEventListener('DOMContentLoaded', () => {
  const portDropdownBtn   = document.getElementById('portDropdownButton');
  const portList          = document.getElementById('port-dropdown');
  const selectedPortInput = document.getElementById('selected-port');
  const tableBody         = document.getElementById('ussd-session-body');

  // Populate SIM ports dropdown with operator name in one line
  fetch('/sim/status/ports')
    .then(resp => resp.json())
    .then(data => {
      portList.innerHTML = '';
      data.forEach(sim => {
        const li  = document.createElement('li');
        const btn = document.createElement('button');
        btn.type         = 'button';
        btn.className    = 'dropdown-item d-flex justify-content-between align-items-center';
        btn.dataset.port = sim.port_number;

        // Single-line display
        const statusIcon = sim.status === 'ONLINE'
          ? '<i class="bi bi-circle-fill text-success"></i>'
          : '<i class="bi bi-circle-fill text-danger"></i>';

        btn.innerHTML = `
          Port ${sim.port_number} — ${sim.sim_number} (${sim.operator_name}) ${statusIcon}
        `;

        btn.addEventListener('click', () => {
          portDropdownBtn.innerHTML = btn.innerHTML;
          selectedPortInput.value   = sim.port_number;
        });

        li.appendChild(btn);
        portList.appendChild(li);
      });
    })
    .catch(err => console.error('Failed to load SIM ports:', err));

  // Refresh USSD sessions table every 5s
  async function refreshSessions() {
    try {
      const resp = await fetch('/ussd/api/sessions');
      const data = await resp.json();
      tableBody.innerHTML = '';
      data.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${s.id}</td>
          <td>${s.port_number}</td>
          <td>${s.code}</td>
          <td>${s.status}</td>
          <td><pre class="mb-0">${s.response}</pre></td>
          <td>${s.created_at}</td>
          <td>${s.completed_at}</td>
        `;
        tableBody.appendChild(tr);
      });
    } catch (e) {
      console.error('Failed to fetch USSD sessions:', e);
    }
  }

  refreshSessions();
  setInterval(refreshSessions, 5000);
});

