import './HomePage.css';

const FEATURE_CARDS = [
  {
    icon: 'vs',
    title: 'Player Comparison Tool',
    description:
      'Compare batters and bowlers head-to-head across 15+ metrics. Filter by phase, venue, and opposition.',
    status: 'coming-soon' as const,
    link: '/comparison',
  },
  {
    icon: 'W',
    title: 'Win Probability Curves',
    description:
      'Ball-by-ball win probability visualization for historical IPL matches. Powered by our gradient-boosted model.',
    status: 'coming-soon' as const,
    link: '/win-probability',
  },
  {
    icon: 'T',
    title: 'Team Deep Dives',
    description:
      'Interactive team profiles with depth charts, predicted XIs, and tournament-weighted form analysis.',
    status: 'coming-soon' as const,
    link: '#',
  },
  {
    icon: 'R',
    title: 'Research Desk',
    description:
      'SQL Lab access to 163 analytics views. Query ball-by-ball data from 2008-2025 directly in your browser.',
    status: 'coming-soon' as const,
    link: '#',
  },
];

const KEY_INSIGHTS = [
  { title: 'Top Scoring Team', value: 'RCB', comparison: '+14.2 avg run rate vs league', trend: 'up' as const },
  { title: 'Best Strike Rate', value: '157.4', comparison: 'Suryakumar Yadav', trend: 'up' as const },
  { title: 'Highest Win Prob', value: 'CSK', comparison: '68% pre-tournament model', trend: 'neutral' as const },
];

function HomePage() {
  return (
    <div className="home-page">
      <div className="container">
        {/* Hero Section */}
        <section className="hero" aria-labelledby="hero-heading">
          <div className="hero-badge">Sports Intelligence Platform</div>
          <h1 id="hero-heading" className="hero-title">
            Stat<span className="gradient-text">sledge</span>
          </h1>
          <p className="hero-subtitle">
            IPL 2026 Pre-Tournament Preview
          </p>
          <p className="hero-description">
            Pro team internal prep packaged for public consumption. Explore tournament-weighted
            analytics, player comparisons, and predictive models built on 17 seasons of ball-by-ball
            data.
          </p>
          <div className="hero-search">
            <svg className="hero-search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16ZM19 19l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <input
              type="search"
              placeholder="Search players, teams, or matches..."
              aria-label="Search players, teams, or matches"
            />
          </div>
        </section>

        {/* Stats Banner */}
        <section className="stats-banner" aria-label="Platform statistics">
          <div className="stat-item">
            <span className="stat-value">163</span>
            <span className="stat-label">Analytics Views</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">10</span>
            <span className="stat-label">IPL Teams</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">17</span>
            <span className="stat-label">Seasons of Data</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">200K+</span>
            <span className="stat-label">Ball-by-Ball Records</span>
          </div>
        </section>

        {/* Key Insights */}
        <section className="insights-section" aria-labelledby="insights-heading">
          <h2 id="insights-heading" className="section-title">Key Insights</h2>
          <div className="insights-grid">
            {KEY_INSIGHTS.map((insight) => (
              <div key={insight.title} className="feature-card">
                <p className="stat-label">{insight.title}</p>
                <p className="stat-value" style={{ fontSize: '32px' }}>{insight.value}</p>
                <p style={{
                  fontSize: 'var(--font-meta)',
                  color: insight.trend === 'up' ? 'var(--sl-positive)' : 'var(--text-secondary)',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}>
                  <span aria-hidden="true">{insight.trend === 'up' ? '\u2191' : '\u2192'}</span>
                  {insight.comparison}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Feature Cards */}
        <section className="features" aria-labelledby="features-heading">
          <h2 id="features-heading" className="section-title">Interactive Features</h2>
          <p className="section-subtitle">Analytical tools designed for depth, not distraction.</p>
          <div className="feature-grid">
            {FEATURE_CARDS.map((card) => (
              <a key={card.title} href={card.link} className="feature-card" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div className="feature-icon" aria-hidden="true">{card.icon}</div>
                <h3 className="feature-title">{card.title}</h3>
                <p className="feature-description">{card.description}</p>
                <span className="hero-badge" style={{ alignSelf: 'flex-start', marginBottom: 0 }}>
                  {card.status === 'coming-soon' ? 'Coming Soon' : 'Active'}
                </span>
              </a>
            ))}
          </div>
        </section>

        {/* Architecture Note */}
        <section className="arch-note" aria-labelledby="arch-heading">
          <div className="arch-card">
            <h3 id="arch-heading" className="arch-note-title">Architecture</h3>
            <p className="arch-note-text">
              Built with React 18 + TypeScript + Vite. Data flows from DuckDB analytics pipeline
              through JSON/JS data files into interactive React components. Deployed to GitHub Pages
              alongside the existing static Lab dashboard.
            </p>
            <div className="tech-stack">
              <span className="tech-badge">React 18</span>
              <span className="tech-badge">TypeScript</span>
              <span className="tech-badge">Vite</span>
              <span className="tech-badge">React Router</span>
              <span className="tech-badge">Vitest</span>
              <span className="tech-badge">GitHub Pages</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default HomePage;
