import {
  forwardRef,
  useEffect,
  useRef,
  useCallback,
  type ReactNode,
  type HTMLAttributes,
  type MouseEvent,
} from 'react';
import { createPortal } from 'react-dom';
import styles from './Modal.module.css';

export type ModalSize = 'sm' | 'md' | 'lg';

export interface ModalProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  /** Whether the modal is visible */
  isOpen: boolean;
  /** Called when the modal should close */
  onClose: () => void;
  /** Modal heading */
  title: ReactNode;
  /** Dialog content */
  children: ReactNode;
  /** Width preset */
  size?: ModalSize;
}

const sizeMap: Record<ModalSize, string> = {
  sm: styles.sm,
  md: styles.md,
  lg: styles.lg,
};

export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  ({ isOpen, onClose, title, children, size = 'md', className, ...rest }, ref) => {
    const dialogRef = useRef<HTMLDivElement>(null);
    const previousFocusRef = useRef<Element | null>(null);

    // Focus trap — capture focus inside the modal
    const trapFocus = useCallback((e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      const modal = dialogRef.current;
      if (!modal) return;

      const focusable = modal.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }, []);

    // Close on Escape
    const handleKeyDown = useCallback(
      (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
        trapFocus(e);
      },
      [onClose, trapFocus],
    );

    // Store previous focus, manage listeners
    useEffect(() => {
      if (isOpen) {
        previousFocusRef.current = document.activeElement;
        document.addEventListener('keydown', handleKeyDown);
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        // Focus the dialog itself
        requestAnimationFrame(() => {
          dialogRef.current?.focus();
        });
      }

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        document.body.style.overflow = '';
        // Restore previous focus
        if (previousFocusRef.current instanceof HTMLElement) {
          previousFocusRef.current.focus();
        }
      };
    }, [isOpen, handleKeyDown]);

    // Click outside to close
    const handleOverlayClick = useCallback(
      (e: MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      },
      [onClose],
    );

    if (!isOpen) return null;

    const dialogCls = [styles.dialog, sizeMap[size], className]
      .filter(Boolean)
      .join(' ');

    const modal = (
      <div
        className={styles.overlay}
        onClick={handleOverlayClick}
        aria-hidden="true"
      >
        <div
          ref={(node) => {
            // Merge refs
            (dialogRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
            if (typeof ref === 'function') ref(node);
            else if (ref) (ref as React.MutableRefObject<HTMLDivElement | null>).current = node;
          }}
          className={dialogCls}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          tabIndex={-1}
          {...rest}
        >
          <div className={styles.header}>
            <h2 id="modal-title" className={styles.title}>
              {title}
            </h2>
            <button
              className={styles.closeBtn}
              onClick={onClose}
              aria-label="Close dialog"
              type="button"
            >
              &#x2715;
            </button>
          </div>
          <div className={styles.body}>{children}</div>
        </div>
      </div>
    );

    return createPortal(modal, document.body);
  },
);

Modal.displayName = 'Modal';

export default Modal;
