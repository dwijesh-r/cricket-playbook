/**
 * The Lab - Pressure Performance Metrics
 * IPL 2026 Pre-Season Analytics (TKT-050)
 * Auto-generated: 2026-02-11T23:28:48.960906
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
            { name: "Naman Dhir", srDelta: 19.6, pressureSR: 209.84, overallSR: 175.45, rating: "CLUTCH", confidence: "MEDIUM", pressureBalls: 61, pressureScore: 45.33, deathPressureBalls: 29 },
            { name: "Tilak Varma", srDelta: 6.2, pressureSR: 164.06, overallSR: 154.5, rating: "MODERATE", confidence: "HIGH", pressureBalls: 217, pressureScore: 25.4, deathPressureBalls: 47 },
            { name: "Q de Kock", srDelta: 3.1, pressureSR: 146.94, overallSR: 142.53, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 98, pressureScore: 8.48, deathPressureBalls: 4 },
        ],
        topBowlers: [
            { name: "MJ Santner", pressureBand: "HIGH", economy: 4.35, legalBalls: 40, wickets: 3, dotBallPct: 40.0, rating: "ELITE" },
            { name: "JJ Bumrah", pressureBand: "NEAR_IMPOSSIBLE", economy: 5.17, legalBalls: 65, wickets: 8, dotBallPct: 50.77, rating: "ELITE" },
            { name: "JJ Bumrah", pressureBand: "EXTREME", economy: 5.41, legalBalls: 41, wickets: 2, dotBallPct: 46.34, rating: "ELITE" },
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
            { name: "MS Dhoni", srDelta: 12.4, pressureSR: 169.09, overallSR: 150.38, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 110, pressureScore: 45.32, deathPressureBalls: 98 },
            { name: "RD Gaikwad", srDelta: 9.8, pressureSR: 141.05, overallSR: 128.49, rating: "MODERATE", confidence: "MEDIUM", pressureBalls: 95, pressureScore: 26.2, deathPressureBalls: 2 },
            { name: "S Dube", srDelta: 6.0, pressureSR: 140.19, overallSR: 132.29, rating: "MODERATE", confidence: "HIGH", pressureBalls: 209, pressureScore: 24.65, deathPressureBalls: 60 },
        ],
        topBowlers: [
            { name: "KV Sharma", pressureBand: "NEAR_IMPOSSIBLE", economy: 5.2, legalBalls: 30, wickets: 3, dotBallPct: 46.67, rating: "ELITE" },
            { name: "RD Chahar", pressureBand: "HIGH", economy: 5.91, legalBalls: 65, wickets: 3, dotBallPct: 33.85, rating: "ELITE" },
            { name: "Noor Ahmad", pressureBand: "NEAR_IMPOSSIBLE", economy: 6.22, legalBalls: 54, wickets: 7, dotBallPct: 46.3, rating: "STRONG" },
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
            { name: "JM Sharma", srDelta: 5.6, pressureSR: 174.38, overallSR: 165.17, rating: "MODERATE", confidence: "HIGH", pressureBalls: 121, pressureScore: 19.04, deathPressureBalls: 54 },
            { name: "RM Patidar", srDelta: 7.5, pressureSR: 165.15, overallSR: 153.68, rating: "MODERATE", confidence: "MEDIUM", pressureBalls: 66, pressureScore: 16.17, deathPressureBalls: 3 },
            { name: "V Kohli", srDelta: 2.6, pressureSR: 156.22, overallSR: 152.32, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 217, pressureScore: 10.05, deathPressureBalls: 13 },
        ],
        topBowlers: [
            { name: "Yash Dayal", pressureBand: "EXTREME", economy: 6.35, legalBalls: 34, wickets: 0, dotBallPct: 47.06, rating: "STRONG" },
            { name: "Suyash Sharma", pressureBand: "EXTREME", economy: 6.37, legalBalls: 65, wickets: 0, dotBallPct: 36.92, rating: "STRONG" },
            { name: "KH Pandya", pressureBand: "HIGH", economy: 6.48, legalBalls: 101, wickets: 3, dotBallPct: 35.64, rating: "STRONG" },
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
            { name: "RK Singh", srDelta: 15.1, pressureSR: 168.5, overallSR: 146.38, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 127, pressureScore: 53.17, deathPressureBalls: 60 },
            { name: "MK Pandey", srDelta: 12.9, pressureSR: 128.0, overallSR: 113.33, rating: "CLUTCH", confidence: "MEDIUM", pressureBalls: 75, pressureScore: 30.9, deathPressureBalls: 7 },
            { name: "AM Rahane", srDelta: 2.4, pressureSR: 152.47, overallSR: 148.84, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 162, pressureScore: 8.37, deathPressureBalls: 0 },
        ],
        topBowlers: [
            { name: "SP Narine", pressureBand: "EXTREME", economy: 5.73, legalBalls: 90, wickets: 6, dotBallPct: 42.22, rating: "ELITE" },
            { name: "AS Roy", pressureBand: "HIGH", economy: 6.0, legalBalls: 21, wickets: 1, dotBallPct: 33.33, rating: "ELITE" },
            { name: "C Green", pressureBand: "HIGH", economy: 6.22, legalBalls: 27, wickets: 1, dotBallPct: 33.33, rating: "STRONG" },
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
            { name: "DA Miller", srDelta: 10.9, pressureSR: 165.32, overallSR: 149.04, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 124, pressureScore: 35.3, deathPressureBalls: 25 },
            { name: "N Rana", srDelta: 4.1, pressureSR: 148.35, overallSR: 142.5, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 182, pressureScore: 15.15, deathPressureBalls: 15 },
            { name: "PP Shaw", srDelta: 4.5, pressureSR: 151.56, overallSR: 145.05, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 64, pressureScore: 9.39, deathPressureBalls: 0 },
        ],
        topBowlers: [
            { name: "Kuldeep Yadav", pressureBand: "HIGH", economy: 6.87, legalBalls: 90, wickets: 2, dotBallPct: 26.67, rating: "STRONG" },
            { name: "AR Patel", pressureBand: "HIGH", economy: 7.67, legalBalls: 72, wickets: 3, dotBallPct: 36.11, rating: "AVERAGE" },
            { name: "Kuldeep Yadav", pressureBand: "EXTREME", economy: 7.71, legalBalls: 95, wickets: 3, dotBallPct: 25.26, rating: "AVERAGE" },
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
            { name: "Shashank Singh", srDelta: 6.9, pressureSR: 173.96, overallSR: 162.77, rating: "MODERATE", confidence: "HIGH", pressureBalls: 169, pressureScore: 26.83, deathPressureBalls: 66 },
            { name: "MP Stoinis", srDelta: 5.5, pressureSR: 152.82, overallSR: 144.9, rating: "MODERATE", confidence: "HIGH", pressureBalls: 195, pressureScore: 21.1, deathPressureBalls: 28 },
            { name: "SS Iyer", srDelta: 3.5, pressureSR: 173.42, overallSR: 167.58, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 79, pressureScore: 8.86, deathPressureBalls: 16 },
        ],
        topBowlers: [
            { name: "Harpreet Brar", pressureBand: "HIGH", economy: 6.49, legalBalls: 61, wickets: 5, dotBallPct: 37.7, rating: "STRONG" },
            { name: "Arshdeep Singh", pressureBand: "EXTREME", economy: 6.97, legalBalls: 93, wickets: 6, dotBallPct: 49.46, rating: "STRONG" },
            { name: "Vijaykumar Vyshak", pressureBand: "EXTREME", economy: 7.06, legalBalls: 17, wickets: 1, dotBallPct: 29.41, rating: "STRONG" },
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
            { name: "RA Jadeja", srDelta: 6.8, pressureSR: 159.43, overallSR: 149.34, rating: "MODERATE", confidence: "HIGH", pressureBalls: 175, pressureScore: 28.01, deathPressureBalls: 99 },
            { name: "R Parag", srDelta: 4.4, pressureSR: 163.37, overallSR: 156.46, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 243, pressureScore: 18.58, deathPressureBalls: 38 },
            { name: "Dhruv Jurel", srDelta: 1.1, pressureSR: 159.32, overallSR: 157.6, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 236, pressureScore: 4.88, deathPressureBalls: 98 },
        ],
        topBowlers: [
            { name: "Sandeep Sharma", pressureBand: "HIGH", economy: 6.79, legalBalls: 91, wickets: 2, dotBallPct: 35.16, rating: "STRONG" },
            { name: "RA Jadeja", pressureBand: "EXTREME", economy: 7.43, legalBalls: 63, wickets: 6, dotBallPct: 25.4, rating: "STRONG" },
            { name: "Sandeep Sharma", pressureBand: "EXTREME", economy: 7.64, legalBalls: 22, wickets: 1, dotBallPct: 9.09, rating: "AVERAGE" },
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
            { name: "H Klaasen", srDelta: 0.8, pressureSR: 162.32, overallSR: 160.98, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 207, pressureScore: 3.43, deathPressureBalls: 60 },
            { name: "LS Livingstone", srDelta: 0.0, pressureSR: 175.0, overallSR: 175.0, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 112, pressureScore: 0.0, deathPressureBalls: 44 },
            { name: "Abhishek Sharma", srDelta: -5.3, pressureSR: 198.13, overallSR: 209.31, rating: "MODERATE", confidence: "HIGH", pressureBalls: 214, pressureScore: -20.68, deathPressureBalls: 7 },
        ],
        topBowlers: [
            { name: "Abhishek Sharma", pressureBand: "HIGH", economy: 7.35, legalBalls: 31, wickets: 1, dotBallPct: 22.58, rating: "STRONG" },
            { name: "E Malinga", pressureBand: "NEAR_IMPOSSIBLE", economy: 7.94, legalBalls: 34, wickets: 5, dotBallPct: 47.06, rating: "AVERAGE" },
            { name: "Nithish Kumar Reddy", pressureBand: "NEAR_IMPOSSIBLE", economy: 8.08, legalBalls: 26, wickets: 2, dotBallPct: 23.08, rating: "AVERAGE" },
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
            { name: "Shubman Gill", srDelta: 16.0, pressureSR: 164.06, overallSR: 141.42, rating: "CLUTCH", confidence: "HIGH", pressureBalls: 217, pressureScore: 62.82, deathPressureBalls: 13 },
            { name: "B Sai Sudharsan", srDelta: 3.9, pressureSR: 147.45, overallSR: 141.85, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 274, pressureScore: 16.6, deathPressureBalls: 3 },
            { name: "JC Buttler", srDelta: 3.2, pressureSR: 152.6, overallSR: 147.8, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 192, pressureScore: 12.5, deathPressureBalls: 30 },
        ],
        topBowlers: [
            { name: "M Prasidh Krishna", pressureBand: "EXTREME", economy: 4.5, legalBalls: 16, wickets: 1, dotBallPct: 56.25, rating: "ELITE" },
            { name: "Arshad Khan", pressureBand: "HIGH", economy: 4.67, legalBalls: 18, wickets: 1, dotBallPct: 61.11, rating: "ELITE" },
            { name: "M Prasidh Krishna", pressureBand: "NEAR_IMPOSSIBLE", economy: 4.9, legalBalls: 60, wickets: 7, dotBallPct: 48.33, rating: "ELITE" },
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
            { name: "A Badoni", srDelta: 4.8, pressureSR: 135.21, overallSR: 129.03, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 142, pressureScore: 17.14, deathPressureBalls: 49 },
            { name: "RR Pant", srDelta: 3.9, pressureSR: 144.32, overallSR: 138.86, rating: "PRESSURE_PROOF", confidence: "MEDIUM", pressureBalls: 88, pressureScore: 10.52, deathPressureBalls: 14 },
            { name: "N Pooran", srDelta: 2.6, pressureSR: 200.58, overallSR: 195.45, rating: "PRESSURE_PROOF", confidence: "HIGH", pressureBalls: 172, pressureScore: 10.08, deathPressureBalls: 52 },
        ],
        topBowlers: [
            { name: "Mohammed Shami", pressureBand: "NEAR_IMPOSSIBLE", economy: 6.33, legalBalls: 36, wickets: 3, dotBallPct: 30.56, rating: "STRONG" },
            { name: "DS Rathi", pressureBand: "HIGH", economy: 7.34, legalBalls: 58, wickets: 2, dotBallPct: 36.21, rating: "STRONG" },
            { name: "DS Rathi", pressureBand: "EXTREME", economy: 7.45, legalBalls: 29, wickets: 2, dotBallPct: 31.03, rating: "STRONG" },
        ]
    },
};
