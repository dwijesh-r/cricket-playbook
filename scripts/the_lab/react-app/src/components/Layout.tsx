import { useState, useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import './Layout.css';

const NAV_ITEMS = [
  { path: '/', label: 'Home' },
  { path: '/comparison', label: 'Comparison' },
  { path: '/win-probability', label: 'Win Probability' },
];

function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 8);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMobileMenu = () => {
    setMobileMenuOpen((prev) => !prev);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="layout">
      {/* Skip navigation for accessibility */}
      <a href="#main-content" className="skip-nav">
        Skip to main content
      </a>

      <nav className={`nav ${scrolled ? 'scrolled' : ''}`} aria-label="Main navigation">
        <div className="nav-brand">
          <div className="nav-logo" aria-hidden="true">S</div>
          <div className="nav-title">
            Stat<span>sledge</span>
          </div>
        </div>

        <div className="nav-tabs" role="menubar">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
              role="menuitem"
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        <button
          className={`mobile-menu-btn ${mobileMenuOpen ? 'active' : ''}`}
          onClick={toggleMobileMenu}
          aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-nav-menu"
          type="button"
        >
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </button>

        <div className="nav-actions">
          <a
            href="https://www.statsledge.com/"
            className="nav-btn"
            title="Back to Statsledge"
          >
            Statsledge
          </a>
        </div>
      </nav>

      {mobileMenuOpen && (
        <div id="mobile-nav-menu" className="mobile-nav-menu active" role="menu">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
              onClick={closeMobileMenu}
              role="menuitem"
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      )}

      <main id="main-content" className="main-content">
        <Outlet />
      </main>

      <footer className="footer" role="contentinfo">
        <div className="container">
          <p className="footer-text">
            Statsledge v5.0.0 &middot; IPL 2026 Pre-Tournament Preview
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
