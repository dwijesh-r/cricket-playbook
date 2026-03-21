// Statsledge Shared JavaScript
// Theme toggle, mobile nav, clock, sidebar collapse

function throttle(fn, ms) { let last = 0; return function() { const now = Date.now(); if (now - last >= ms) { last = now; fn.apply(this, arguments); } }; }

function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
}

function toggleTheme() {
    const html = document.documentElement;
    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    const btn = document.querySelector('.theme-toggle');
    if (btn) {
        btn.textContent = newTheme === 'dark' ? '\u{1F319}' : '\u{2600}\u{FE0F}';
        btn.setAttribute('aria-label', newTheme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    }
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-nav-menu');
    const btn = document.querySelector('.mobile-menu-btn');
    if (!menu || !btn) return;
    const isOpen = menu.classList.toggle('active');
    btn.classList.toggle('active');
    btn.setAttribute('aria-expanded', isOpen);
}

// Close mobile menu on outside click
document.addEventListener('click', function(e) {
    const menu = document.getElementById('mobile-nav-menu');
    const btn = document.querySelector('.mobile-menu-btn');
    if (menu && menu.classList.contains('active') && !menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.remove('active');
        btn.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
    }
});

// Theme restore + clock
document.addEventListener('DOMContentLoaded', function() {
    // Restore theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        const btn = document.querySelector('.theme-toggle');
        if (btn) btn.textContent = savedTheme === 'dark' ? '\u{1F319}' : '\u{2600}\u{FE0F}';
    }
    // Restore sidebar state
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        var sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.add('collapsed');
    }
    // Double-click sidebar logo to collapse/expand
    var brand = document.querySelector('.sidebar-brand');
    if (brand) {
        brand.addEventListener('dblclick', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }
    // Clock
    const clockEl = document.getElementById('navTime');
    if (clockEl) {
        function updateTime() {
            clockEl.textContent = new Date().toLocaleTimeString('en-US', { hour12: false });
        }
        updateTime();
        setInterval(updateTime, 1000);
    }
});
