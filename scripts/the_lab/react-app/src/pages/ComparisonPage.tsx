import './PageCommon.css';

/**
 * ComparisonPage - Player Comparison Tool
 *
 * Future implementation will load data from comparison_data.js
 * (located at ../dashboard/data/comparison_data.js) and provide
 * interactive head-to-head comparisons across metrics like:
 * - Strike rate by phase (powerplay, middle, death)
 * - Boundary percentage
 * - Average vs specific bowling types
 * - Venue-specific performance
 * - Tournament-weighted form
 */
function ComparisonPage() {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <span className="badge badge--coming-soon">Coming Soon</span>
          <h1 className="page-title">Player Comparison Tool</h1>
          <p className="page-subtitle">
            Compare any two IPL players head-to-head across 15+ tournament-weighted metrics.
          </p>
        </div>

        <div className="placeholder-section">
          <div className="card placeholder-card">
            <div className="placeholder-icon">vs</div>
            <h2 className="placeholder-heading">Interactive Comparison Engine</h2>
            <p className="placeholder-text">
              This tool will allow you to select any two batters or bowlers and compare them across
              multiple dimensions including phase-wise performance, matchup history, venue splits,
              and cluster-based profiling.
            </p>

            <div className="placeholder-features">
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">1</span>
                <div>
                  <strong>Select Players</strong>
                  <p>Choose from all IPL 2026 squad members with autocomplete search.</p>
                </div>
              </div>
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">2</span>
                <div>
                  <strong>Pick Metrics</strong>
                  <p>Filter by phase, venue, opposition, and time period.</p>
                </div>
              </div>
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">3</span>
                <div>
                  <strong>Visualize</strong>
                  <p>Radar charts, bar comparisons, and trend lines with tournament weighting.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="data-source-note">
          <p>
            Data source: <code>comparison_data.js</code> &middot; 289 KB &middot; Generated from
            163 analytics views
          </p>
        </div>
      </div>
    </div>
  );
}

export default ComparisonPage;
