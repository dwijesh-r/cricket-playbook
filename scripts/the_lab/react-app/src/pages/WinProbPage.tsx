import './PageCommon.css';

/**
 * WinProbPage - Win Probability Visualization
 *
 * Future implementation will display ball-by-ball win probability
 * curves for historical IPL matches. The model uses gradient-boosted
 * trees trained on match context features:
 * - Current run rate vs required rate
 * - Wickets in hand
 * - Phase of innings
 * - Venue-specific scoring patterns
 * - Batting/bowling matchup strength
 */
function WinProbPage() {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <span className="badge badge--coming-soon">Coming Soon</span>
          <h1 className="page-title">Win Probability Curves</h1>
          <p className="page-subtitle">
            Ball-by-ball win probability visualization for historical IPL matches.
          </p>
        </div>

        <div className="placeholder-section">
          <div className="card placeholder-card">
            <div className="placeholder-icon">W</div>
            <h2 className="placeholder-heading">Match Win Probability Engine</h2>
            <p className="placeholder-text">
              Select any historical IPL match and see how the win probability shifted ball by ball.
              Our gradient-boosted model captures the momentum swings that make T20 cricket
              compelling, from powerplay domination to death-over heroics.
            </p>

            <div className="placeholder-features">
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">1</span>
                <div>
                  <strong>Select Match</strong>
                  <p>Browse by season, team, or search for specific matches from 2008-2025.</p>
                </div>
              </div>
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">2</span>
                <div>
                  <strong>View Probability Curve</strong>
                  <p>
                    Interactive line chart showing win% for each team, ball by ball, with key moment
                    annotations.
                  </p>
                </div>
              </div>
              <div className="placeholder-feature">
                <span className="placeholder-feature-icon">3</span>
                <div>
                  <strong>Analyze Key Moments</strong>
                  <p>
                    Identify the biggest probability swings: wickets, boundaries, and turning points.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="data-source-note">
          <p>
            Model: Gradient-boosted trees &middot; Features: match context + venue + matchup
            strength &middot; Training data: 1,100+ IPL matches
          </p>
        </div>
      </div>
    </div>
  );
}

export default WinProbPage;
