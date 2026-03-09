/**
 * Confidential Toggle — floating button for individual report pages.
 * Detects auth via /api/auth-check, shows toggle to flip confidential status.
 */
(function() {
  const pathname = window.location.pathname;
  const filename = pathname.split('/').pop() || '';
  if (!filename || filename === 'index.html' || !filename.endsWith('.html')) return;

  fetch('/api/auth-check')
    .then(r => r.json())
    .then(data => {
      if (!data.authenticated) return;
      // Fetch manifest to get current state
      return fetch('/manifest.json?v=' + Date.now())
        .then(r => r.json())
        .then(manifest => {
          const report = manifest.reports.find(r => r.file === filename);
          if (!report) return;
          createFloatingButton(report.confidential || false);
        });
    })
    .catch(() => {});

  function createFloatingButton(isConfidential) {
    const btn = document.createElement('button');
    btn.id = 'confidential-toggle-btn';
    updateButton(btn, isConfidential);

    const style = document.createElement('style');
    style.textContent = `
      #confidential-toggle-btn {
        position: fixed; bottom: 24px; right: 24px; z-index: 9999;
        font-family: 'Manrope', sans-serif; font-size: 0.8125rem; font-weight: 600;
        padding: 10px 18px; border: 1px solid oklch(0.32 0.005 260);
        background: oklch(0.18 0.005 260 / 0.95); color: oklch(0.85 0 0);
        cursor: pointer; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        transition: all 0.25s ease; display: flex; align-items: center; gap: 8px;
      }
      #confidential-toggle-btn:hover { border-color: oklch(0.72 0.12 192); color: oklch(0.92 0 0); }
      #confidential-toggle-btn.is-confidential { border-color: oklch(0.55 0.10 50 / 0.6); }
    `;
    document.head.appendChild(style);
    document.body.appendChild(btn);

    btn.addEventListener('click', async () => {
      btn.disabled = true;
      btn.style.opacity = '0.5';
      try {
        const res = await fetch('/api/toggle-confidential', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file: filename })
        });
        const result = await res.json();
        if (result.ok) updateButton(btn, result.confidential);
      } catch (e) { console.error('Toggle failed:', e); }
      btn.disabled = false;
      btn.style.opacity = '1';
    });
  }

  function updateButton(btn, isConfidential) {
    btn.innerHTML = isConfidential ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="oklch(0.7 0.15 25)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:5px;"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>Confidential' : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:5px;"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>Public';
    btn.className = isConfidential ? 'is-confidential' : '';
    btn.id = 'confidential-toggle-btn';
  }
})();
