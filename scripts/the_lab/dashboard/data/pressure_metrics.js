/**
 * The Lab - Pressure Performance Metrics
 * IPL 2026 Pre-Season Analytics (TKT-050)
 * Auto-generated: 2026-02-12T07:45:49.956643
 * Source: analytics_ipl_pressure_deltas_since2023,
 *         analytics_ipl_batter_pressure_bands_since2023,
 *         analytics_ipl_bowler_pressure_bands_since2023
 */

const PRESSURE_DATA = {
    MI: {
        summary: {
            clutch: 1,
            pressureProof: 3,
            pressureSensitive: 0,
            moderate: 4,
            total: 8,
            clutchScore: 5.4
        },
        topBatters: [
            { name: "Naman Dhir", srDelta: 19.6, pressureSR: 209.84, overallSR: 175.45, rating: "CLUTCH", confidence: "MEDIUM", pressureBalls: 61, pressureScore: 45.33, deathPressureBalls: 29, entryContext: "FRESH" },
            { name: "Tilak Varma", srDelta: 6.2, pressureSR: 164.06, overallSR: 154.5, rating: "MODERATE", confidence: "HIGH", pressureBalls: 217, pressureScore: 25.4, deathPressureBalls: 47, entryContext: "BUILDING" },
            { name: "Q de Kock", srDelta: 3.1, pressureSR: 146.94, overallSR: 142.53, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 98, pressureScore: 8.48, deathPressureBalls: 4, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "MJ Santner", pressureBand: "EXTREME", economy: 5.92, legalBalls: 72, wickets: 5, dotBallPct: 36.11, rating: "ELITE" },
            { name: "JJ Bumrah", pressureBand: "NEAR_IMPOSSIBLE", economy: 6.13, legalBalls: 183, wickets: 16, dotBallPct: 48.09, rating: "STRONG" },
            { name: "C Bosch", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.71, legalBalls: 35, wickets: 1, dotBallPct: 54.28, rating: "AVERAGE" },
        ]
    },
    CSK: {
        summary: {
            clutch: 1,
            pressureProof: 1,
            pressureSensitive: 0,
            moderate: 2,
            total: 4,
            clutchScore: 5.8
        },
        topBatters: [
            { name: "MS Dhoni", srDelta: 12.4, pressureSR: 169.09, overallSR: 150.38, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 110, pressureScore: 45.32, deathPressureBalls: 98, entryContext: "FRESH" },
            { name: "RD Gaikwad", srDelta: 9.8, pressureSR: 141.05, overallSR: 128.49, rating: "MODERATE", confidence: "MEDIUM", pressureBalls: 95, pressureScore: 26.2, deathPressureBalls: 2, entryContext: "BUILDING" },
            { name: "S Dube", srDelta: 6.0, pressureSR: 140.19, overallSR: 132.29, rating: "MODERATE", confidence: "HIGH", pressureBalls: 209, pressureScore: 24.65, deathPressureBalls: 60, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "RD Chahar", pressureBand: "EXTREME", economy: 7.53, legalBalls: 122, wickets: 4, dotBallPct: 31.15, rating: "AVERAGE" },
            { name: "AJ Hosein", pressureBand: "HIGH", economy: 8.53, legalBalls: 19, wickets: 1, dotBallPct: 26.32, rating: "AVERAGE" },
            { name: "NT Ellis", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.56, legalBalls: 129, wickets: 11, dotBallPct: 29.46, rating: "AVERAGE" },
        ]
    },
    RCB: {
        summary: {
            clutch: 0,
            pressureProof: 3,
            pressureSensitive: 2,
            moderate: 4,
            total: 9,
            clutchScore: 2.2
        },
        topBatters: [
            { name: "JM Sharma", srDelta: 5.6, pressureSR: 174.38, overallSR: 165.17, rating: "MODERATE", confidence: "HIGH", pressureBalls: 121, pressureScore: 19.04, deathPressureBalls: 54, entryContext: "FRESH" },
            { name: "RM Patidar", srDelta: 7.5, pressureSR: 165.15, overallSR: 153.68, rating: "MODERATE", confidence: "MEDIUM", pressureBalls: 66, pressureScore: 16.17, deathPressureBalls: 3, entryContext: "FRESH" },
            { name: "V Kohli", srDelta: 2.6, pressureSR: 156.22, overallSR: 152.32, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 217, pressureScore: 10.05, deathPressureBalls: 13, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "MP Yadav", pressureBand: "HIGH", economy: 6.62, legalBalls: 29, wickets: 3, dotBallPct: 51.72, rating: "STRONG" },
            { name: "KH Pandya", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.51, legalBalls: 179, wickets: 7, dotBallPct: 35.19, rating: "AVERAGE" },
            { name: "JR Hazlewood", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.44, legalBalls: 91, wickets: 8, dotBallPct: 50.55, rating: "AVERAGE" },
        ]
    },
    KKR: {
        summary: {
            clutch: 2,
            pressureProof: 5,
            pressureSensitive: 1,
            moderate: 1,
            total: 9,
            clutchScore: 5.6
        },
        topBatters: [
            { name: "RK Singh", srDelta: 15.1, pressureSR: 168.5, overallSR: 146.38, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 127, pressureScore: 53.17, deathPressureBalls: 60, entryContext: "BUILDING" },
            { name: "MK Pandey", srDelta: 12.9, pressureSR: 128.0, overallSR: 113.33, rating: "CLUTCH", confidence: "MEDIUM", pressureBalls: 75, pressureScore: 30.9, deathPressureBalls: 7, entryContext: "BUILDING" },
            { name: "AM Rahane", srDelta: 2.4, pressureSR: 152.47, overallSR: 148.84, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 162, pressureScore: 8.37, deathPressureBalls: 0, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "SP Narine", pressureBand: "NEAR_IMPOSSIBLE", economy: 6.92, legalBalls: 287, wickets: 16, dotBallPct: 35.89, rating: "STRONG" },
            { name: "C Green", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.78, legalBalls: 91, wickets: 5, dotBallPct: 34.06, rating: "AVERAGE" },
            { name: "M Pathirana", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.26, legalBalls: 231, wickets: 19, dotBallPct: 37.23, rating: "AVERAGE" },
        ]
    },
    DC: {
        summary: {
            clutch: 1,
            pressureProof: 7,
            pressureSensitive: 0,
            moderate: 1,
            total: 9,
            clutchScore: 6.7
        },
        topBatters: [
            { name: "DA Miller", srDelta: 10.9, pressureSR: 165.32, overallSR: 149.04, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 124, pressureScore: 35.3, deathPressureBalls: 25, entryContext: "FRESH" },
            { name: "N Rana", srDelta: 4.1, pressureSR: 148.35, overallSR: 142.5, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 182, pressureScore: 15.15, deathPressureBalls: 15, entryContext: "BUILDING" },
            { name: "PP Shaw", srDelta: 4.5, pressureSR: 151.56, overallSR: 145.05, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 64, pressureScore: 9.39, deathPressureBalls: 0, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "Kuldeep Yadav", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.76, legalBalls: 232, wickets: 9, dotBallPct: 25.86, rating: "AVERAGE" },
            { name: "L Ngidi", pressureBand: "HIGH", economy: 7.91, legalBalls: 22, wickets: 2, dotBallPct: 36.36, rating: "AVERAGE" },
            { name: "AR Patel", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.58, legalBalls: 156, wickets: 6, dotBallPct: 28.2, rating: "AVERAGE" },
        ]
    },
    PBKS: {
        summary: {
            clutch: 0,
            pressureProof: 1,
            pressureSensitive: 0,
            moderate: 4,
            total: 5,
            clutchScore: 4.0
        },
        topBatters: [
            { name: "Shashank Singh", srDelta: 6.9, pressureSR: 173.96, overallSR: 162.77, rating: "MODERATE", confidence: "HIGH", pressureBalls: 169, pressureScore: 26.83, deathPressureBalls: 66, entryContext: "BUILDING" },
            { name: "MP Stoinis", srDelta: 5.5, pressureSR: 152.82, overallSR: 144.9, rating: "MODERATE", confidence: "HIGH", pressureBalls: 195, pressureScore: 21.1, deathPressureBalls: 28, entryContext: "BUILDING" },
            { name: "SS Iyer", srDelta: 3.5, pressureSR: 173.42, overallSR: 167.58, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 79, pressureScore: 8.86, deathPressureBalls: 16, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "Harpreet Brar", pressureBand: "EXTREME", economy: 7.23, legalBalls: 102, wickets: 6, dotBallPct: 33.33, rating: "STRONG" },
            { name: "YS Chahal", pressureBand: "NEAR_IMPOSSIBLE", economy: 9.0, legalBalls: 256, wickets: 18, dotBallPct: 28.13, rating: "AVERAGE" },
            { name: "Arshdeep Singh", pressureBand: "NEAR_IMPOSSIBLE", economy: 9.24, legalBalls: 272, wickets: 14, dotBallPct: 40.07, rating: "VULNERABLE" },
        ]
    },
    RR: {
        summary: {
            clutch: 0,
            pressureProof: 4,
            pressureSensitive: 0,
            moderate: 2,
            total: 6,
            clutchScore: 5.6
        },
        topBatters: [
            { name: "RA Jadeja", srDelta: 6.8, pressureSR: 159.43, overallSR: 149.34, rating: "MODERATE", confidence: "HIGH", pressureBalls: 175, pressureScore: 28.01, deathPressureBalls: 99, entryContext: "BUILDING" },
            { name: "R Parag", srDelta: 4.4, pressureSR: 163.37, overallSR: 156.46, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 243, pressureScore: 18.58, deathPressureBalls: 38, entryContext: "BUILDING" },
            { name: "Dhruv Jurel", srDelta: 1.1, pressureSR: 159.32, overallSR: 157.6, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 236, pressureScore: 4.88, deathPressureBalls: 98, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "Sandeep Sharma", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.67, legalBalls: 165, wickets: 5, dotBallPct: 26.66, rating: "AVERAGE" },
            { name: "RA Jadeja", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.02, legalBalls: 241, wickets: 12, dotBallPct: 28.63, rating: "AVERAGE" },
            { name: "JC Archer", pressureBand: "HIGH", economy: 8.25, legalBalls: 24, wickets: 2, dotBallPct: 45.83, rating: "AVERAGE" },
        ]
    },
    SRH: {
        summary: {
            clutch: 0,
            pressureProof: 2,
            pressureSensitive: 3,
            moderate: 1,
            total: 6,
            clutchScore: 0
        },
        topBatters: [
            { name: "H Klaasen", srDelta: 0.8, pressureSR: 162.32, overallSR: 160.98, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 207, pressureScore: 3.43, deathPressureBalls: 60, entryContext: "BUILDING" },
            { name: "LS Livingstone", srDelta: 0.0, pressureSR: 175.0, overallSR: 175.0, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 112, pressureScore: 0.0, deathPressureBalls: 44, entryContext: "BUILDING" },
            { name: "Abhishek Sharma", srDelta: -5.3, pressureSR: 198.13, overallSR: 209.31, rating: "MODERATE", confidence: "HIGH", pressureBalls: 214, pressureScore: -20.68, deathPressureBalls: 7, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "E Malinga", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.94, legalBalls: 34, wickets: 5, dotBallPct: 47.06, rating: "AVERAGE" },
            { name: "Harsh Dubey", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.5, legalBalls: 24, wickets: 3, dotBallPct: 41.67, rating: "AVERAGE" },
            { name: "Nithish Kumar Reddy", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.83, legalBalls: 53, wickets: 2, dotBallPct: 30.19, rating: "AVERAGE" },
        ]
    },
    GT: {
        summary: {
            clutch: 1,
            pressureProof: 5,
            pressureSensitive: 0,
            moderate: 1,
            total: 7,
            clutchScore: 6.7
        },
        topBatters: [
            { name: "Shubman Gill", srDelta: 16.0, pressureSR: 164.06, overallSR: 141.42, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 217, pressureScore: 62.82, deathPressureBalls: 13, entryContext: "BUILDING" },
            { name: "B Sai Sudharsan", srDelta: 3.9, pressureSR: 147.45, overallSR: 141.85, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 274, pressureScore: 16.6, deathPressureBalls: 3, entryContext: "BUILDING" },
            { name: "JC Buttler", srDelta: 3.2, pressureSR: 152.6, overallSR: 147.8, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 192, pressureScore: 12.5, deathPressureBalls: 30, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "Arshad Khan", pressureBand: "HIGH", economy: 4.67, legalBalls: 18, wickets: 1, dotBallPct: 61.11, rating: "ELITE" },
            { name: "M Prasidh Krishna", pressureBand: "NEAR_IMPOSSIBLE", economy: 5.5, legalBalls: 96, wickets: 9, dotBallPct: 47.91, rating: "ELITE" },
            { name: "GD Phillips", pressureBand: "HIGH", economy: 6.67, legalBalls: 18, wickets: 1, dotBallPct: 33.33, rating: "STRONG" },
        ]
    },
    LSG: {
        summary: {
            clutch: 0,
            pressureProof: 3,
            pressureSensitive: 3,
            moderate: 1,
            total: 7,
            clutchScore: 0.5
        },
        topBatters: [
            { name: "A Badoni", srDelta: 4.8, pressureSR: 135.21, overallSR: 129.03, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 142, pressureScore: 17.14, deathPressureBalls: 49, entryContext: "FRESH" },
            { name: "RR Pant", srDelta: 3.9, pressureSR: 144.32, overallSR: 138.86, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 88, pressureScore: 10.52, deathPressureBalls: 14, entryContext: "BUILDING" },
            { name: "N Pooran", srDelta: 2.6, pressureSR: 200.58, overallSR: 195.45, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 172, pressureScore: 10.08, deathPressureBalls: 52, entryContext: "BUILDING" },
        ],
        topBowlers: [
            { name: "DS Rathi", pressureBand: "EXTREME", economy: 7.38, legalBalls: 87, wickets: 4, dotBallPct: 34.48, rating: "STRONG" },
            { name: "Mohammed Shami", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.18, legalBalls: 165, wickets: 11, dotBallPct: 43.64, rating: "AVERAGE" },
            { name: "M Siddharth", pressureBand: "HIGH", economy: 8.48, legalBalls: 29, wickets: 1, dotBallPct: 44.83, rating: "AVERAGE" },
        ]
    },
};
