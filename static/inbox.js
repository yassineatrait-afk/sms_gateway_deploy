// static/inbox.js

document.addEventListener('DOMContentLoaded', () => {
  const portDropdownBtn   = document.getElementById('portDropdownButton');
  const portList          = document.getElementById('port-dropdown');
  const selectedPortInput = document.getElementById('selected-port');

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

        const statusIcon = sim.status === 'ONLINE'
          ? '<i class="bi bi-circle-fill text-success"></i>'
          : '<i class="bi bi-circle-fill text-danger"></i>';

        btn.innerHTML = `
          Port ${sim.port_number}: ${sim.sim_number} (${sim.operator_name}) ${statusIcon}
        `;

        btn.addEventListener('click', () => {
          portDropdownBtn.innerHTML = btn.innerHTML;
          selectedPortInput.value   = sim.port_number;
        });

        li.appendChild(btn);
        portList.appendChild(li);
      });

      // If page was reloaded with a pre-selected port, re-apply it
      const pre = selectedPortInput.value;
      if (pre) {
        const match = portList.querySelector(`button[data-port="${pre}"]`);
        if (match) match.click();
      }
    })
    .catch(err => console.error('Failed to load SIM ports:', err));
});

