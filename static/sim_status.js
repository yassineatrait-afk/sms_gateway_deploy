document.addEventListener('DOMContentLoaded', () => {
  const portDropdownBtn = document.getElementById('portDropdown');
  const portList = document.getElementById('port-list');
  const selectedPortInput = document.getElementById('selected-port');
  const queueBody = document.getElementById('at-queue-body');
  const commandSelect = document.getElementById('command-select');
  const commandInput = document.getElementById('at-command');

  // Load ports from backend
  fetch('/sim/status/ports')
    .then(resp => resp.json())
    .then(data => {
      portList.innerHTML = ''; // clear

      data.forEach(sim => {
        const iconBars = Math.min(Math.floor((sim.signal_quality || 0) / 8) + 1, 4);
        const icon = sim.status === 'ONLINE'
          ? `<i class="bi bi-signal${iconBars} me-2"></i>`
          : '<i class="bi bi-x-circle text-danger me-2"></i>';

        const item = document.createElement('li');
        item.innerHTML = `
          <button class="dropdown-item d-flex align-items-center" type="button" data-port="${sim.port_number}">
            ${icon} Port ${sim.port_number} ${sim.status !== 'ONLINE' ? '(OFFLINE)' : ''}
          </button>
        `;
        portList.appendChild(item);
      });

      // Attach click listeners
      portList.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
          const port = btn.getAttribute('data-port');
          portDropdownBtn.textContent = btn.textContent;
          selectedPortInput.value = port;
        });
      });
    });

  // Keep dropdown and input in sync
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

  // Load command queue
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
    } catch (err) {
      console.error('Refresh AT queue failed:', err);
    }
  }

  refreshQueue();
  setInterval(refreshQueue, 5000);
});

