-- IPL_2026_Final_Version: Authoritative merged view of Founder Review + Squad + Contracts + Experience
CREATE OR REPLACE VIEW IPL_2026_Final_Version AS
SELECT
    fs.team_abbrev,
    fs.team_name,
    fs.squad_number,
    fs.player_name,
    fs.player_id,
    fs.role,
    fs.batting_hand,
    fs.bowling_arm,
    fs.bowling_type,
    fs.age,
    fs.nationality,
    fs.is_predicted_xii,
    fs.batting_position,
    fs.notes AS founder_notes,
    fs.price_cr,
    fs.ipl_matches,
    fs.ipl_batting_runs,
    fs.ipl_batting_sr,
    fs.ipl_bowling_wickets,
    fs.ipl_bowling_economy,
    sq.batter_classification,
    sq.bowler_classification,
    sq.batter_tags,
    sq.bowler_tags,
    sq.is_captain
FROM founder_squads_2026 fs
LEFT JOIN ipl_2026_squads sq ON fs.player_id = sq.player_id;
