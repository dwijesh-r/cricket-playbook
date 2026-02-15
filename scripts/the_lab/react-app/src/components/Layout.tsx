import { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import './Layout.css';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard' },
  { path: '/comparison', label: 'Comparison' },
  { path: '/win-probability', label: 'Win Probability' },
];

function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen((prev) => !prev);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="layout">
      <nav className="nav">
        <div className="nav-brand">
          <div className="nav-logo">P</div>
          <div className="nav-title">
            Cricket <span>Playbook</span>
          </div>
        </div>

        <div className="nav-tabs">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        <button
          className={`mobile-menu-btn ${mobileMenuOpen ? 'active' : ''}`}
          onClick={toggleMobileMenu}
          aria-label="Toggle navigation menu"
        >
          <span />
          <span />
          <span />
        </button>

        <div className="nav-actions">
          <a
            href="https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/"
            className="nav-btn"
            title="Back to Static Lab"
          >
            Static Lab
          </a>
        </div>
      </nav>

      {mobileMenuOpen && (
        <div className="mobile-nav-menu active">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      )}

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="container">
          <p className="footer-text">
            Cricket Playbook v5.0.0 &middot; IPL 2026 Pre-Tournament Preview
          </p>
          <p className="footer-sub">
            Built with data from{' '}
            <a href="https://cricsheet.org" target="_blank" rel="noopener noreferrer">
              Cricsheet
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
