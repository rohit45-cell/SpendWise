/* SpendWise Pro — Main JS */

document.addEventListener('DOMContentLoaded', () => {

  // ── Theme Toggle ───────────────────────────────────────────
  const themeBtn = document.getElementById('themeToggle');
  const html = document.documentElement;

  const savedTheme = localStorage.getItem('sw-theme') || 'light';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', async () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('sw-theme', next);
      updateThemeIcon(next);

      // Sync with server if logged in
      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
          || getCookie('csrftoken');
        if (csrfToken) {
          await fetch('/api/toggle-theme/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' }
          });
        }
      } catch (e) {}
    });
  }

  function updateThemeIcon(theme) {
    if (!themeBtn) return;
    themeBtn.innerHTML = theme === 'dark'
      ? '<i class="fas fa-sun"></i>'
      : '<i class="fas fa-moon"></i>';
  }

  // ── Sidebar Toggle (Mobile) ────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay?.classList.toggle('show');
    });

    overlay?.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // ── Auto-dismiss Alerts ────────────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    closeBtn?.addEventListener('click', () => dismissAlert(alert));
    setTimeout(() => dismissAlert(alert), 5000);
  });

  function dismissAlert(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    el.style.transition = 'all 0.3s ease';
    setTimeout(() => el.remove(), 300);
  }

  // ── Animated Counters ──────────────────────────────────────
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.getAttribute('data-count'));
    const currency = el.getAttribute('data-currency') || '';
    const duration = 1200;
    const start = performance.now();

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = target * eased;
      el.textContent = currency + formatNumber(current);
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  });

  function formatNumber(n) {
    if (n >= 100000) return (n / 100000).toFixed(2) + 'L';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toFixed(0);
  }

  // ── CSRF Cookie Helper ─────────────────────────────────────
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ── Stagger animation for table rows ──────────────────────
  document.querySelectorAll('tbody tr, .transaction-item').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.04}s`;
    el.style.animation = 'slideIn 0.35s ease backwards';
  });

  // ── Stat card entry animation ──────────────────────────────
  document.querySelectorAll('.stat-card').forEach((card, i) => {
    card.style.animationDelay = `${i * 0.08}s`;
  });

  // ── Form submit loading state ──────────────────────────────
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        setTimeout(() => {
          submitBtn.disabled = true;
          const originalText = submitBtn.innerHTML;
          submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
          // Re-enable after 5s as fallback
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
          }, 5000);
        }, 0);
      }
    });
  });

  // ── Active nav item ────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item[href]').forEach(item => {
    if (item.getAttribute('href') === currentPath ||
        (item.getAttribute('href') !== '/' && currentPath.startsWith(item.getAttribute('href')))) {
      item.classList.add('active');
    }
  });

  // ── Date default for forms ─────────────────────────────────
  document.querySelectorAll('input[type="date"]').forEach(input => {
    if (!input.value) {
      const today = new Date().toISOString().split('T')[0];
      input.value = today;
    }
  });
});
