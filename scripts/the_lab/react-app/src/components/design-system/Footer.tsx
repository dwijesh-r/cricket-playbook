import { forwardRef, type HTMLAttributes } from 'react';
import styles from './Footer.module.css';

export interface FooterLink {
  /** Link display text */
  label: string;
  /** Link URL */
  href: string;
}

export interface FooterSection {
  /** Section heading */
  title: string;
  /** Links in this section */
  links: FooterLink[];
}

export interface FooterProps extends HTMLAttributes<HTMLElement> {
  /** Footer column sections */
  sections?: FooterSection[];
}

const currentYear = new Date().getFullYear();

export const Footer = forwardRef<HTMLElement, FooterProps>(
  ({ sections, className, ...rest }, ref) => {
    const cls = [styles.footer, className].filter(Boolean).join(' ');

    return (
      <footer ref={ref} className={cls} role="contentinfo" {...rest}>
        <div className={styles.inner}>
          {/* Column sections */}
          {sections && sections.length > 0 && (
            <div className={styles.grid}>
              {sections.map((section) => (
                <div key={section.title} className={styles.column}>
                  <h3 className={styles.columnTitle}>{section.title}</h3>
                  <ul className={styles.linkList}>
                    {section.links.map((link) => (
                      <li key={link.href}>
                        <a
                          href={link.href}
                          className={styles.link}
                          aria-label={link.label}
                        >
                          {link.label}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {/* Copyright */}
          <div className={styles.copyright}>
            <p>
              &copy; {currentYear} Statsledge. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    );
  },
);

Footer.displayName = 'Footer';

export default Footer;
