// static/at_command.js

document.addEventListener('DOMContentLoaded', () => {
  const portSelect    = document.getElementById('port-select');
  const commandSelect = document.getElementById('command-select');
  const commandInput  = document.getElementById('at-command');
  const queueBody     = document.getElementById('at-queue-body');

  // Load ports (unchanged)
  fetch('/sim/status/ports')
    .then(r => r.json())
    .then(data => {
      portSelect.innerHTML = '<option value=\"\">-- Choisissez un port --</option>';
      data.forEach(sim => {
        const opt = document.createElement('option');
        opt.value = sim.port_number;
        opt.text  = `Port ${sim.port_number}`;
        portSelect.appendChild(opt);
      });
    });

  // Sync command dropdown & input
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

  // --- NEW: refresh AT-queue table ---
  async function refreshQueue() {
    try {
      const resp = await fetch('/at/api/commands');
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();

      // rebuild body
      queueBody.innerHTML = '';
      data.forEach(cmd => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${cmd.id}</td>
          <td>${cmd.port_number}</td>
          <td><code>${cmd.command_text}</code></td>
          <td>${cmd.created_at}</td>
          <td>
            ${cmd.status === 0
              ? '<span class="badge bg-warning text-dark">En attente</span>'
              : '<span class="badge bg-success">Exécutée</span>'}
          </td>
          <td>${cmd.executed_at}</td>
          <td><pre class="mb-0">${cmd.result}</pre></td>
        `;
        queueBody.appendChild(tr);
      });
    } catch (e) {
      console.error('Failed to refresh AT queue:', e);
    }
  }

  // initial load + interval
  refreshQueue();
  setInterval(refreshQueue, 5000);
});

