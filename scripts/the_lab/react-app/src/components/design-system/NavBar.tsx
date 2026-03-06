import {
  forwardRef,
  useState,
  useEffect,
  useCallback,
  type HTMLAttributes,
  type ReactNode,
  type KeyboardEvent,
} from 'react';
import styles from './NavBar.module.css';

export interface NavItem {
  /** Display label */
  label: string;
  /** Navigation path / href */
  path: string;
}

export interface NavBarProps extends Omit<HTMLAttributes<HTMLElement>, 'children'> {
  /** Navigation items */
  items: NavItem[];
  /** Logo element rendered on the left */
  logo?: ReactNode;
  /** Action elements rendered on the right (e.g., search, profile) */
  actions?: ReactNode;
  /** Currently active path — used to highlight the active nav item */
  activePath?: string;
}

export const NavBar = forwardRef<HTMLElement, NavBarProps>(
  ({ items, logo, actions, activePath, className, ...rest }, ref) => {
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
      const handleScroll = () => {
        setScrolled(window.scrollY > 8);
      };
      window.addEventListener('scroll', handleScroll, { passive: true });
      return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleMenu = useCallback(() => {
      setMenuOpen((prev) => !prev);
    }, []);

    const closeMenu = useCallback(() => {
      setMenuOpen(false);
    }, []);

    const handleHamburgerKeyDown = useCallback(
      (e: KeyboardEvent<HTMLButtonElement>) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleMenu();
        }
      },
      [toggleMenu],
    );

    const cls = [styles.nav, scrolled ? styles.scrolled : '', className]
      .filter(Boolean)
      .join(' ');

    return (
      <nav ref={ref} className={cls} aria-label="Main navigation" {...rest}>
        <div className={styles.inner}>
          {/* Logo */}
          {logo && <div className={styles.logo}>{logo}</div>}

          {/* Desktop nav items */}
          <ul className={styles.items} role="menubar">
            {items.map((item) => {
              const isActive = activePath === item.path;
              const linkCls = [styles.link, isActive ? styles.active : '']
                .filter(Boolean)
                .join(' ');

              return (
                <li key={item.path} role="none">
                  <a
                    href={item.path}
                    className={linkCls}
                    role="menuitem"
                    aria-current={isActive ? 'page' : undefined}
                  >
                    {item.label}
                    {isActive && (
                      <span className={styles.activeIndicator} aria-hidden="true" />
                    )}
                  </a>
                </li>
              );
            })}
          </ul>

          {/* Actions */}
          {actions && <div className={styles.actions}>{actions}</div>}

          {/* Hamburger button (mobile) */}
          <button
            className={styles.hamburger}
            onClick={toggleMenu}
            onKeyDown={handleHamburgerKeyDown}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            aria-controls="navbar-mobile-menu"
            type="button"
          >
            <span className={[styles.bar, menuOpen ? styles.barOpen : ''].filter(Boolean).join(' ')} aria-hidden="true" />
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <ul
            id="navbar-mobile-menu"
            className={styles.mobileMenu}
            role="menu"
          >
            {items.map((item) => {
              const isActive = activePath === item.path;
              const linkCls = [styles.mobileLink, isActive ? styles.active : '']
                .filter(Boolean)
                .join(' ');

              return (
                <li key={item.path} role="none">
                  <a
                    href={item.path}
                    className={linkCls}
                    role="menuitem"
                    aria-current={isActive ? 'page' : undefined}
                    onClick={closeMenu}
                  >
                    {item.label}
                  </a>
                </li>
              );
            })}
          </ul>
        )}
      </nav>
    );
  },
);

NavBar.displayName = 'NavBar';

export default NavBar;
