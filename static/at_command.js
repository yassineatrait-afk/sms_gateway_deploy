// static/at_command.js

document.addEventListener('DOMContentLoaded', () => {
  const portDropdownBtn   = document.getElementById('portDropdownButton');
  const portList          = document.getElementById('port-dropdown');
  const selectedPortInput = document.getElementById('selected-port');
  const commandSelect     = document.getElementById('command-select');
  const commandInput      = document.getElementById('at-command');
  const queueBody         = document.getElementById('at-queue-body');

  // --- Load SIM ports into the Bootstrap dropdown with operator ---
  fetch('/sim/status/ports')
    .then(resp => resp.json())
    .then(data => {
      portList.innerHTML = '';  // clear existing

      data.forEach(sim => {
        const li  = document.createElement('li');
        const btn = document.createElement('button');
        btn.type         = 'button';
        btn.className    = 'dropdown-item d-flex justify-content-between align-items-center';
        btn.dataset.port = sim.port_number;

        // Single-line display: Port — Number (Operator) + status icon
        const statusIcon = sim.status === 'ONLINE'
          ? '<i class="bi bi-circle-fill text-success"></i>'
          : '<i class="bi bi-circle-fill text-danger"></i>';

        btn.innerHTML = `
          Port ${sim.port_number} — ${sim.sim_number} (${sim.operator_name}) ${statusIcon}
        `;

        btn.addEventListener('click', () => {
          // Update dropdown button HTML and hidden input value
          portDropdownBtn.innerHTML   = btn.innerHTML;
          selectedPortInput.value     = sim.port_number;
        });

        li.appendChild(btn);
        portList.appendChild(li);
      });
    })
    .catch(err => console.error('Failed to load SIM ports:', err));

  // --- Keep AT‐command select & input in sync ---
  commandSelect.addEventListener('change', () => {
    commandInput.value = commandSelect.value;
  });
  commandInput.addEventListener('input', () => {
    const val = commandInput.value.trim();
    if ([...commandSelect.options].some(o => o.value === val)) {
      commandSelect.value = val;
    } else {
      commandSelect.value = '';
    }
  });

  // --- Refresh AT‐command history every 5s ---
  async function refreshQueue() {
    try {
      const resp = await fetch('/at/api/commands');
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();

      queueBody.innerHTML = '';
      data.forEach(cmd => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${cmd.id}</td>
          <td>${cmd.port_number}</td>
          <td><code>${cmd.command_text}</code></td>
          <td>${cmd.created_at}</td>
          <td>${
            cmd.status === 0
              ? '<span class="badge bg-warning text-dark">En attente</span>'
              : '<span class="badge bg-success">Exécutée</span>'
          }</td>
          <td>${cmd.executed_at}</td>
          <td><pre class="mb-0">${cmd.result}</pre></td>
        `;
        queueBody.appendChild(tr);
      });
    } catch (e) {
      console.error('Failed to refresh AT queue:', e);
    }
  }

  // Initial load + interval
  refreshQueue();
  setInterval(refreshQueue, 5000);
});
