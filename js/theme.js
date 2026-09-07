// js/theme.js
// 다크 모드 토글 및 선택 저장 (보너스 과제: UX 고도화)

(function () {
  const STORAGE_KEY = 'news-summary-bot-theme';
  const root = document.documentElement;

  function applyTheme(theme, toggleBtn) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
      if (toggleBtn) {
        toggleBtn.textContent = '☀️';
        toggleBtn.setAttribute('aria-label', '라이트 모드로 전환');
      }
    } else {
      root.removeAttribute('data-theme');
      if (toggleBtn) {
        toggleBtn.textContent = '🌙';
        toggleBtn.setAttribute('aria-label', '다크 모드로 전환');
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('theme-toggle');

    // 우선순위: 사용자가 이전에 선택한 값 > 시스템(OS) 다크모드 설정 > 기본(라이트)
    const saved = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(saved || (prefersDark ? 'dark' : 'light'), toggleBtn);

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        const isDark = root.getAttribute('data-theme') === 'dark';
        const next = isDark ? 'light' : 'dark';
        applyTheme(next, toggleBtn);
        localStorage.setItem(STORAGE_KEY, next);
      });
    }
  });
})();
