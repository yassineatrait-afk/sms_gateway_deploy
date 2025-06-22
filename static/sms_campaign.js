document.addEventListener('DOMContentLoaded', () => {
  const msgField = document.getElementById('message');
  const charCount = document.getElementById('charCount');
  const progressBar = document.getElementById('msgProgress');

  msgField.addEventListener('input', () => {
    const len = msgField.value.length;
    const smsCount = Math.ceil(len / 160);
    const percent = (len % 160) / 160 * 100;
    charCount.textContent = `${len} caractère(s) / ${smsCount} message(s)`;
    progressBar.style.width = `${percent}%`;
  });

  // Toggle scheduled datetime
  const scheduleRadios = document.querySelectorAll('input[name="schedule_type"]');
  const schedInputWrapper = document.querySelector('.schedule-field');
  scheduleRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      schedInputWrapper.classList.toggle('d-none', radio.value !== 'scheduled');
    });
  });
});
