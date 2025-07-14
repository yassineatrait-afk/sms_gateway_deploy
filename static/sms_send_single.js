// static/sms_send_single.js

document.addEventListener('DOMContentLoaded', () => {
  const portDropdownBtn   = document.getElementById('portDropdownButton');
  const portList          = document.getElementById('port-dropdown');
  const selectedPortInput = document.getElementById('selected-port');
  const form              = document.querySelector('form');
  const loadingSpinner    = document.getElementById('loadingSpinner');

  // Populate SIM‐ports dropdown (single-line: port — number (operator) + status icon)
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

  // Show spinner on submit
  form.addEventListener('submit', () => {
    loadingSpinner.classList.remove('d-none');
  });
});
