import {
  forwardRef,
  useRef,
  useState,
  useEffect,
  useCallback,
  type HTMLAttributes,
  type KeyboardEvent,
} from 'react';
import styles from './Tabs.module.css';

export interface TabItem {
  /** Unique key for this tab */
  key: string;
  /** Display label */
  label: string;
}

export interface TabsProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onChange'> {
  /** Tab definitions */
  tabs: TabItem[];
  /** Currently active tab key */
  activeKey: string;
  /** Called when a tab is selected */
  onChange: (key: string) => void;
}

export const Tabs = forwardRef<HTMLDivElement, TabsProps>(
  ({ tabs, activeKey, onChange, className, ...rest }, ref) => {
    const tabListRef = useRef<HTMLDivElement>(null);
    const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());
    const [indicatorStyle, setIndicatorStyle] = useState<{
      left: number;
      width: number;
    }>({ left: 0, width: 0 });

    // Update indicator position when activeKey changes
    useEffect(() => {
      const el = tabRefs.current.get(activeKey);
      const container = tabListRef.current;
      if (el && container) {
        const containerRect = container.getBoundingClientRect();
        const elRect = el.getBoundingClientRect();
        setIndicatorStyle({
          left: elRect.left - containerRect.left,
          width: elRect.width,
        });
      }
    }, [activeKey, tabs]);

    const handleKeyDown = useCallback(
      (e: KeyboardEvent<HTMLButtonElement>) => {
        const currentIdx = tabs.findIndex((t) => t.key === activeKey);
        let nextIdx: number | null = null;

        if (e.key === 'ArrowRight') {
          nextIdx = (currentIdx + 1) % tabs.length;
        } else if (e.key === 'ArrowLeft') {
          nextIdx = (currentIdx - 1 + tabs.length) % tabs.length;
        } else if (e.key === 'Home') {
          nextIdx = 0;
        } else if (e.key === 'End') {
          nextIdx = tabs.length - 1;
        }

        if (nextIdx !== null) {
          e.preventDefault();
          const nextTab = tabs[nextIdx];
          onChange(nextTab.key);
          tabRefs.current.get(nextTab.key)?.focus();
        }
      },
      [tabs, activeKey, onChange],
    );

    const wrapperCls = [className].filter(Boolean).join(' ');

    return (
      <div ref={ref} className={wrapperCls} {...rest}>
        <div
          ref={tabListRef}
          className={styles.tabList}
          role="tablist"
          aria-orientation="horizontal"
        >
          {tabs.map((tab) => {
            const isActive = tab.key === activeKey;
            const btnCls = [styles.tab, isActive ? styles.tabActive : '']
              .filter(Boolean)
              .join(' ');

            return (
              <button
                key={tab.key}
                ref={(el) => {
                  if (el) tabRefs.current.set(tab.key, el);
                }}
                className={btnCls}
                role="tab"
                id={`tab-${tab.key}`}
                aria-selected={isActive}
                aria-controls={`tabpanel-${tab.key}`}
                tabIndex={isActive ? 0 : -1}
                onClick={() => onChange(tab.key)}
                onKeyDown={handleKeyDown}
              >
                {tab.label}
              </button>
            );
          })}
          <span
            className={styles.indicator}
            style={{
              left: `${indicatorStyle.left}px`,
              width: `${indicatorStyle.width}px`,
            }}
            aria-hidden="true"
          />
        </div>
      </div>
    );
  },
);

Tabs.displayName = 'Tabs';

/**
 * TabPanel — wraps content for a specific tab. Render alongside <Tabs>.
 *
 * Usage:
 *   <Tabs tabs={tabs} activeKey={active} onChange={setActive} />
 *   <TabPanel tabKey="overview" activeKey={active}>...content...</TabPanel>
 */
export interface TabPanelProps extends HTMLAttributes<HTMLDivElement> {
  tabKey: string;
  activeKey: string;
}

export const TabPanel = forwardRef<HTMLDivElement, TabPanelProps>(
  ({ tabKey, activeKey, children, className, ...rest }, ref) => {
    if (tabKey !== activeKey) return null;

    const cls = [styles.panel, className].filter(Boolean).join(' ');

    return (
      <div
        ref={ref}
        className={cls}
        role="tabpanel"
        id={`tabpanel-${tabKey}`}
        aria-labelledby={`tab-${tabKey}`}
        tabIndex={0}
        {...rest}
      >
        {children}
      </div>
    );
  },
);

TabPanel.displayName = 'TabPanel';

export default Tabs;
