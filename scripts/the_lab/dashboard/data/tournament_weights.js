/**
 * The Lab - Tournament Quality Weights (Phase 1)
 * IPL 2026 Pre-Season Analytics (TKT-183/187)
 * Auto-generated from: outputs/tournament_composite_weights_phase1.json
 * Computed: 2026-02-12T02:35:25.077253+00:00
 * Owner: Jose Mourinho (Quant Researcher)
 *
 * Formula: Geometric mean of 5 weighted factors
 * Decay half-life: 4 years | Reference year: 2026
 * Conditions baseline: IPL 2023-2025
 */

var TOURNAMENT_WEIGHTS = {
    metadata: {
        formula: "geometric_mean",
        decayHalflifeYears: 4.0,
        conditionsBaseline: "IPL 2023-2025",
        computedAt: "2026-02-12T02:35:25.077253+00:00",
        ticket: "TKT-187",
        owner: "Jose Mourinho",
        factorWeights: {
            pqi: 0.25,
            effective_ci: 0.20,
            recency: 0.20,
            conditions_similarity: 0.15,
            sample_confidence: 0.20
        },
        totalTopIplPlayers: 220,
        referenceYear: 2026
    },
    tournaments: [
        {
            tournament: "Indian Premier League",
            key: "indian_premier_league",
            compositeWeight: 0.8721,
            tier: "1A",
            factors: { pqi: 1.0, effective_ci: 0.5311, recency: 1.0, conditions_similarity: 1.0, sample_confidence: 0.95 },
            seasonsAnalyzed: 18,
            totalMatches: 1169
        },
        {
            tournament: "Syed Mushtaq Ali Trophy",
            key: "syed_mushtaq_ali_trophy",
            compositeWeight: 0.6603,
            tier: "1B",
            factors: { pqi: 0.5682, effective_ci: 0.3598, recency: 0.8409, conditions_similarity: 0.85, sample_confidence: 0.95 },
            seasonsAnalyzed: 9,
            totalMatches: 695
        },
        {
            tournament: "Big Bash League",
            key: "big_bash_league",
            compositeWeight: 0.5261,
            tier: "1C",
            factors: { pqi: 0.2136, effective_ci: 0.4911, recency: 1.0, conditions_similarity: 0.5, sample_confidence: 0.95 },
            seasonsAnalyzed: 15,
            totalMatches: 654
        },
        {
            tournament: "Pakistan Super League",
            key: "pakistan_super_league",
            compositeWeight: 0.514,
            tier: "1C",
            factors: { pqi: 0.1818, effective_ci: 0.4864, recency: 0.9033, conditions_similarity: 0.65, sample_confidence: 0.95 },
            seasonsAnalyzed: 11,
            totalMatches: 314
        },
        {
            tournament: "The Hundred",
            key: "the_hundred_mens_competition",
            compositeWeight: 0.5035,
            tier: "1C",
            factors: { pqi: 0.2227, effective_ci: 0.5305, recency: 1.0, conditions_similarity: 0.4, sample_confidence: 0.7925 },
            seasonsAnalyzed: 5,
            totalMatches: 167
        },
        {
            tournament: "SA20",
            key: "sa20",
            compositeWeight: 0.5021,
            tier: "1C",
            factors: { pqi: 0.2455, effective_ci: 0.4791, recency: 1.0, conditions_similarity: 0.55, sample_confidence: 0.6035 },
            seasonsAnalyzed: 4,
            totalMatches: 121
        },
        {
            tournament: "ICC Men's T20 World Cup",
            key: "icc_mens_t20_world_cup",
            compositeWeight: 0.4984,
            tier: "1C",
            factors: { pqi: 0.3591, effective_ci: 0.3965, recency: 0.7596, conditions_similarity: 0.5, sample_confidence: 0.6177 },
            seasonsAnalyzed: 3,
            totalMatches: 124
        },
        {
            tournament: "Vitality Blast",
            key: "vitality_blast",
            compositeWeight: 0.4976,
            tier: "1C",
            factors: { pqi: 0.2, effective_ci: 0.5198, recency: 0.8409, conditions_similarity: 0.45, sample_confidence: 0.95 },
            seasonsAnalyzed: 7,
            totalMatches: 835
        },
        {
            tournament: "Caribbean Premier League",
            key: "caribbean_premier_league",
            compositeWeight: 0.4967,
            tier: "1C",
            factors: { pqi: 0.1727, effective_ci: 0.4808, recency: 1.0, conditions_similarity: 0.5, sample_confidence: 0.95 },
            seasonsAnalyzed: 13,
            totalMatches: 407
        },
        {
            tournament: "International League T20",
            key: "international_league_t20",
            compositeWeight: 0.4889,
            tier: "1C",
            factors: { pqi: 0.2136, effective_ci: 0.4535, recency: 1.0, conditions_similarity: 0.55, sample_confidence: 0.6637 },
            seasonsAnalyzed: 4,
            totalMatches: 134
        },
        {
            tournament: "Major League Cricket",
            key: "major_league_cricket",
            compositeWeight: 0.4233,
            tier: "2",
            factors: { pqi: 0.2091, effective_ci: 0.4637, recency: 1.0, conditions_similarity: 0.45, sample_confidence: 0.3775 },
            seasonsAnalyzed: 3,
            totalMatches: 75
        },
        {
            tournament: "Lanka Premier League",
            key: "lanka_premier_league",
            compositeWeight: 0.3982,
            tier: "2",
            factors: { pqi: 0.1, effective_ci: 0.5227, recency: 0.8409, conditions_similarity: 0.6, sample_confidence: 0.5939 },
            seasonsAnalyzed: 5,
            totalMatches: 119
        },
        {
            tournament: "CSA T20 Challenge",
            key: "csa_t20_challenge",
            compositeWeight: 0.3834,
            tier: "2",
            factors: { pqi: 0.0727, effective_ci: 0.5469, recency: 0.8409, conditions_similarity: 0.55, sample_confidence: 0.7465 },
            seasonsAnalyzed: 7,
            totalMatches: 154
        },
        {
            tournament: "Super Smash",
            key: "super_smash",
            compositeWeight: 0.3633,
            tier: "2",
            factors: { pqi: 0.0545, effective_ci: 0.5024, recency: 1.0, conditions_similarity: 0.4, sample_confidence: 0.95 },
            seasonsAnalyzed: 9,
            totalMatches: 256
        }
    ],
    conditionsReasoning: {
        indian_premier_league: "Baseline. IPL conditions are the reference standard.",
        syed_mushtaq_ali_trophy: "Same Indian grounds and pitch types, but lower-quality outfields, smaller crowds, and domestic-level pressure. Strong conditions overlap; lower intensity.",
        pakistan_super_league: "Subcontinent venue profile with similar spinning conditions and heat. Key differences: Pakistan pitches tend to be slower and lower-scoring.",
        lanka_premier_league: "Subcontinent with spin-friendly conditions. Sri Lankan pitches offer more turn and are generally slower than IPL surfaces.",
        sa20: "Pace-friendly South African wickets differ substantially from Indian conditions. Higher bounce, more seam movement, different ball behavior.",
        big_bash_league: "Australian conditions: harder, bouncier pitches with bigger boundaries. Different ball (Kookaburra vs SG).",
        caribbean_premier_league: "Caribbean pitches can be slow and low, somewhat similar to subcontinent. But smaller grounds, different climate, and variable pitch quality.",
        international_league_t20: "UAE conditions: flat batting surfaces. Some similarity to Indian flat tracks but different dew factor and ball behavior.",
        the_hundred_mens_competition: "100-ball format is structurally different from T20. English conditions (seam, overcast) are fundamentally unlike Indian batting paradises.",
        major_league_cricket: "American venues with drop-in pitches and unfamiliar conditions. Still T20 format but conditions are non-transferable.",
        vitality_blast: "English county grounds with seaming/swinging conditions. Very different from Indian conditions despite being full T20 format.",
        csa_t20_challenge: "Same South African conditions as SA20 but domestic-level. Pace-friendly wickets, higher bounce. Limited overlap with Indian conditions.",
        super_smash: "New Zealand conditions: green tops, seam movement. Very different pitch behavior from India. Limited transferability.",
        icc_mens_t20_world_cup: "Varies by host country. Average across host conditions is moderate similarity."
    }
};
