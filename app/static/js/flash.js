document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('flash-messages');
  if (!container) return;

  const items = container.querySelectorAll('.flash-item');

  // Animate in + schedule auto-dismiss
  items.forEach((item, i) => {
    // fade-in (staggered)
    setTimeout(() => {
      item.classList.remove('opacity-0', '-translate-y-2');
      item.classList.add('opacity-100', 'translate-y-0');
    }, 100 * i);

    // auto-dismiss
    const timeout = Number(item.dataset.timeout || 4000);
    setTimeout(() => hide(item), timeout + i * 200);
  });

  // Event delegation for dismiss clicks
  container.addEventListener('click', (e) => {
    const btn = e.target.closest('.dismiss-btn');
    if (!btn) return;
    const item = btn.closest('.flash-item');
    hide(item, true);
  });

  // Hide with fade-out, then remove from DOM
  function hide(item, immediate = false) {
    if (!item || item.dataset.hiding) return;
    item.dataset.hiding = '1';
    item.classList.remove('opacity-100', 'translate-y-0');
    item.classList.add('opacity-0', '-translate-y-2');
    setTimeout(() => {
      if (item && item.parentNode) item.parentNode.removeChild(item);
    }, immediate ? 150 : 300); // match your transition duration
  }
});
