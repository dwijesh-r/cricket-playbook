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

function HomePage() {
  return (
    <div className="home-page">
      <div className="container">
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-badge badge badge--active">React Dashboard</div>
          <h1 className="hero-title">
            Cricket <span className="gradient-text">Playbook</span>
          </h1>
          <p className="hero-subtitle">
            IPL 2026 Pre-Tournament Preview &middot; Interactive Dashboard
          </p>
          <p className="hero-description">
            Pro team internal prep packaged for public consumption. Explore tournament-weighted
            analytics, player comparisons, and predictive models built on 17 seasons of ball-by-ball
            data.
          </p>
        </section>

        {/* Stats Banner */}
        <section className="stats-banner">
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

        {/* Feature Cards */}
        <section className="features">
          <h2 className="section-title">Interactive Features</h2>
          <div className="feature-grid">
            {FEATURE_CARDS.map((card) => (
              <div key={card.title} className="card feature-card">
                <div className="feature-icon">{card.icon}</div>
                <h3 className="feature-title">{card.title}</h3>
                <p className="feature-description">{card.description}</p>
                <span className={`badge badge--${card.status}`}>
                  {card.status === 'coming-soon' ? 'Coming Soon' : 'Active'}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Architecture Note */}
        <section className="arch-note">
          <div className="card">
            <h3 className="arch-note-title">Architecture</h3>
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
