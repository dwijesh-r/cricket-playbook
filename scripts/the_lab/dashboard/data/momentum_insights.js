/**
 * The Lab - Momentum & Pressure Sequence Insights
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: 2026-02-13T14:44:35.608329+00:00
 * Source: analytics_ipl_pressure_dot_sequences_since2023,
 *         analytics_ipl_pressure_boundary_sequences_since2023,
 *         analytics_ipl_pressure_deltas_since2023
 * Owner: Andy Flower (Cricket Domain Expert)
 */

var MOMENTUM_INSIGHTS = {
    "metadata": {
        "computedAt": "2026-02-13T14:44:35.608329+00:00",
        "source": "analytics_ipl_pressure_dot/boundary_sequences_since2023 + pressure_deltas_since2023",
        "owner": "Andy Flower (Cricket Domain Expert)"
    },
    "teams": {
        "MI": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "TA Boult",
                        "dotSequences": 17,
                        "avgLength": 2.9,
                        "maxLength": 6
                    },
                    {
                        "name": "JJ Bumrah",
                        "dotSequences": 20,
                        "avgLength": 2.6,
                        "maxLength": 5
                    },
                    {
                        "name": "C Bosch",
                        "dotSequences": 5,
                        "avgLength": 2.6,
                        "maxLength": 4
                    }
                ],
                "teamTotalSequences": 101,
                "bestMaxStreak": 6
            },
            "battingResilience": {
                "rating": "Average",
                "topBatters": [
                    {
                        "name": "Tilak Varma",
                        "boundarySequences": 6,
                        "avgLength": 2.5,
                        "maxLength": 4
                    },
                    {
                        "name": "SA Yadav",
                        "boundarySequences": 12,
                        "avgLength": 2.5,
                        "maxLength": 4
                    },
                    {
                        "name": "HH Pandya",
                        "boundarySequences": 5,
                        "avgLength": 2.4,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 46,
                "bestMaxStreak": 4
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "Naman Dhir",
                        "normalSR": 175.4,
                        "pressureSR": 209.8,
                        "delta": "+19.6"
                    },
                    {
                        "name": "Tilak Varma",
                        "normalSR": 154.5,
                        "pressureSR": 164.1,
                        "delta": "+6.2"
                    },
                    {
                        "name": "Q de Kock",
                        "normalSR": 142.5,
                        "pressureSR": 146.9,
                        "delta": "+3.1"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "WG Jacks",
                        "normalSR": 159.0,
                        "pressureSR": 143.2,
                        "delta": "-10.0"
                    },
                    {
                        "name": "SA Yadav",
                        "normalSR": 184.6,
                        "pressureSR": 169.9,
                        "delta": "-8.0"
                    },
                    {
                        "name": "SE Rutherford",
                        "normalSR": 161.0,
                        "pressureSR": 151.8,
                        "delta": "-5.7"
                    }
                ],
                "teamAvgDelta": 0.8
            },
            "andyFlowerInsight": "MI lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.9. Counter-attack capability is limited -- Tilak Varma leads with just 2.5 avg boundary sequence length. Key vulnerability: WG Jacks's SR drops 10% under pressure -- opposition will target this window."
        },
        "CSK": {
            "bowlingPressure": {
                "rating": "Average",
                "topBowlers": [
                    {
                        "name": "RD Chahar",
                        "dotSequences": 4,
                        "avgLength": 3.0,
                        "maxLength": 5
                    },
                    {
                        "name": "KK Ahmed",
                        "dotSequences": 13,
                        "avgLength": 2.8,
                        "maxLength": 6
                    },
                    {
                        "name": "Noor Ahmad",
                        "dotSequences": 12,
                        "avgLength": 2.5,
                        "maxLength": 5
                    }
                ],
                "teamTotalSequences": 50,
                "bestMaxStreak": 6
            },
            "battingResilience": {
                "rating": "Explosive",
                "topBatters": [
                    {
                        "name": "A Mhatre",
                        "boundarySequences": 2,
                        "avgLength": 4.0,
                        "maxLength": 6
                    },
                    {
                        "name": "SV Samson",
                        "boundarySequences": 11,
                        "avgLength": 2.4,
                        "maxLength": 3
                    },
                    {
                        "name": "MS Dhoni",
                        "boundarySequences": 3,
                        "avgLength": 2.0,
                        "maxLength": 2
                    }
                ],
                "teamTotalSequences": 24,
                "bestMaxStreak": 6
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "MS Dhoni",
                        "normalSR": 150.4,
                        "pressureSR": 169.1,
                        "delta": "+12.4"
                    },
                    {
                        "name": "RD Gaikwad",
                        "normalSR": 128.5,
                        "pressureSR": 141.1,
                        "delta": "+9.8"
                    },
                    {
                        "name": "S Dube",
                        "normalSR": 132.3,
                        "pressureSR": 140.2,
                        "delta": "+6.0"
                    }
                ],
                "chokeRisks": [],
                "teamAvgDelta": 8.2
            },
            "andyFlowerInsight": "CSK lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 3.0. Counter-attack capability led by A Mhatre (6 consecutive boundaries under pressure)."
        },
        "RCB": {
            "bowlingPressure": {
                "rating": "Average",
                "topBowlers": [
                    {
                        "name": "JR Hazlewood",
                        "dotSequences": 13,
                        "avgLength": 3.0,
                        "maxLength": 5
                    },
                    {
                        "name": "MP Yadav",
                        "dotSequences": 7,
                        "avgLength": 2.7,
                        "maxLength": 5
                    },
                    {
                        "name": "B Kumar",
                        "dotSequences": 20,
                        "avgLength": 2.5,
                        "maxLength": 5
                    }
                ],
                "teamTotalSequences": 75,
                "bestMaxStreak": 5
            },
            "battingResilience": {
                "rating": "Strong",
                "topBatters": [
                    {
                        "name": "TH David",
                        "boundarySequences": 2,
                        "avgLength": 3.0,
                        "maxLength": 3
                    },
                    {
                        "name": "V Kohli",
                        "boundarySequences": 7,
                        "avgLength": 2.1,
                        "maxLength": 3
                    },
                    {
                        "name": "D Padikkal",
                        "boundarySequences": 2,
                        "avgLength": 2.0,
                        "maxLength": 2
                    }
                ],
                "teamTotalSequences": 24,
                "bestMaxStreak": 3
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "RM Patidar",
                        "normalSR": 153.7,
                        "pressureSR": 165.2,
                        "delta": "+7.5"
                    },
                    {
                        "name": "JM Sharma",
                        "normalSR": 165.2,
                        "pressureSR": 174.4,
                        "delta": "+5.6"
                    },
                    {
                        "name": "V Kohli",
                        "normalSR": 152.3,
                        "pressureSR": 156.2,
                        "delta": "+2.6"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "D Padikkal",
                        "normalSR": 129.9,
                        "pressureSR": 106.1,
                        "delta": "-18.3"
                    },
                    {
                        "name": "PD Salt",
                        "normalSR": 181.3,
                        "pressureSR": 160.0,
                        "delta": "-11.7"
                    },
                    {
                        "name": "VR Iyer",
                        "normalSR": 150.9,
                        "pressureSR": 138.2,
                        "delta": "-8.4"
                    }
                ],
                "teamAvgDelta": -3.7
            },
            "andyFlowerInsight": "RCB lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 3.0. Counter-attack capability led by TH David (3 consecutive boundaries under pressure). Key vulnerability: D Padikkal's SR drops 18% under pressure -- opposition will target this window."
        },
        "KKR": {
            "bowlingPressure": {
                "rating": "Strong",
                "topBowlers": [
                    {
                        "name": "VG Arora",
                        "dotSequences": 6,
                        "avgLength": 3.5,
                        "maxLength": 6
                    },
                    {
                        "name": "C Green",
                        "dotSequences": 4,
                        "avgLength": 2.8,
                        "maxLength": 3
                    },
                    {
                        "name": "Akash Deep",
                        "dotSequences": 4,
                        "avgLength": 2.5,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 96,
                "bestMaxStreak": 6
            },
            "battingResilience": {
                "rating": "Strong",
                "topBatters": [
                    {
                        "name": "R Ravindra",
                        "boundarySequences": 2,
                        "avgLength": 3.0,
                        "maxLength": 3
                    },
                    {
                        "name": "R Powell",
                        "boundarySequences": 2,
                        "avgLength": 2.5,
                        "maxLength": 3
                    },
                    {
                        "name": "MK Pandey",
                        "boundarySequences": 2,
                        "avgLength": 2.5,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 28,
                "bestMaxStreak": 3
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "RK Singh",
                        "normalSR": 146.4,
                        "pressureSR": 168.5,
                        "delta": "+15.1"
                    },
                    {
                        "name": "MK Pandey",
                        "normalSR": 113.3,
                        "pressureSR": 128.0,
                        "delta": "+12.9"
                    },
                    {
                        "name": "AM Rahane",
                        "normalSR": 148.8,
                        "pressureSR": 152.5,
                        "delta": "+2.4"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "R Powell",
                        "normalSR": 149.1,
                        "pressureSR": 134.0,
                        "delta": "-10.1"
                    },
                    {
                        "name": "SP Narine",
                        "normalSR": 177.3,
                        "pressureSR": 166.7,
                        "delta": "-6.0"
                    },
                    {
                        "name": "A Raghuvanshi",
                        "normalSR": 126.5,
                        "pressureSR": 121.9,
                        "delta": "-3.7"
                    }
                ],
                "teamAvgDelta": 0.7
            },
            "andyFlowerInsight": "KKR's pressure game is anchored by VG Arora's dot-ball sequences (avg 3.5 consecutive dots under high RRR). Counter-attack capability led by R Ravindra (3 consecutive boundaries under pressure). Key vulnerability: R Powell's SR drops 10% under pressure -- opposition will target this window."
        },
        "DC": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "T Natarajan",
                        "dotSequences": 8,
                        "avgLength": 2.8,
                        "maxLength": 4
                    },
                    {
                        "name": "Mukesh Kumar",
                        "dotSequences": 8,
                        "avgLength": 2.4,
                        "maxLength": 4
                    },
                    {
                        "name": "Kuldeep Yadav",
                        "dotSequences": 11,
                        "avgLength": 2.2,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 46,
                "bestMaxStreak": 4
            },
            "battingResilience": {
                "rating": "Strong",
                "topBatters": [
                    {
                        "name": "KK Nair",
                        "boundarySequences": 2,
                        "avgLength": 3.0,
                        "maxLength": 4
                    },
                    {
                        "name": "N Rana",
                        "boundarySequences": 6,
                        "avgLength": 2.7,
                        "maxLength": 6
                    },
                    {
                        "name": "PP Shaw",
                        "boundarySequences": 5,
                        "avgLength": 2.6,
                        "maxLength": 4
                    }
                ],
                "teamTotalSequences": 42,
                "bestMaxStreak": 6
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "DA Miller",
                        "normalSR": 149.0,
                        "pressureSR": 165.3,
                        "delta": "+10.9"
                    },
                    {
                        "name": "PP Shaw",
                        "normalSR": 145.1,
                        "pressureSR": 151.6,
                        "delta": "+4.5"
                    },
                    {
                        "name": "N Rana",
                        "normalSR": 142.5,
                        "pressureSR": 148.3,
                        "delta": "+4.1"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "Abishek Porel",
                        "normalSR": 132.0,
                        "pressureSR": 119.8,
                        "delta": "-9.2"
                    },
                    {
                        "name": "KL Rahul",
                        "normalSR": 135.5,
                        "pressureSR": 129.6,
                        "delta": "-4.4"
                    }
                ],
                "teamAvgDelta": 1.0
            },
            "andyFlowerInsight": "DC lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.8. Counter-attack capability led by KK Nair (4 consecutive boundaries under pressure). Key vulnerability: Abishek Porel's SR drops 9% under pressure -- opposition will target this window."
        },
        "PBKS": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "LH Ferguson",
                        "dotSequences": 6,
                        "avgLength": 2.8,
                        "maxLength": 4
                    },
                    {
                        "name": "Yash Thakur",
                        "dotSequences": 8,
                        "avgLength": 2.6,
                        "maxLength": 5
                    },
                    {
                        "name": "Arshdeep Singh",
                        "dotSequences": 25,
                        "avgLength": 2.6,
                        "maxLength": 4
                    }
                ],
                "teamTotalSequences": 83,
                "bestMaxStreak": 5
            },
            "battingResilience": {
                "rating": "Limited",
                "topBatters": [
                    {
                        "name": "P Simran Singh",
                        "boundarySequences": 3,
                        "avgLength": 2.3,
                        "maxLength": 3
                    },
                    {
                        "name": "Shashank Singh",
                        "boundarySequences": 5,
                        "avgLength": 2.2,
                        "maxLength": 3
                    },
                    {
                        "name": "MP Stoinis",
                        "boundarySequences": 5,
                        "avgLength": 2.2,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 16,
                "bestMaxStreak": 3
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "Shashank Singh",
                        "normalSR": 162.8,
                        "pressureSR": 174.0,
                        "delta": "+6.9"
                    },
                    {
                        "name": "MP Stoinis",
                        "normalSR": 144.9,
                        "pressureSR": 152.8,
                        "delta": "+5.5"
                    },
                    {
                        "name": "SS Iyer",
                        "normalSR": 167.6,
                        "pressureSR": 173.4,
                        "delta": "+3.5"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "P Simran Singh",
                        "normalSR": 147.7,
                        "pressureSR": 134.6,
                        "delta": "-8.9"
                    },
                    {
                        "name": "N Wadhera",
                        "normalSR": 142.9,
                        "pressureSR": 133.1,
                        "delta": "-6.8"
                    }
                ],
                "teamAvgDelta": 0.0
            },
            "andyFlowerInsight": "PBKS lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.8. Counter-attack capability is limited -- P Simran Singh leads with just 2.3 avg boundary sequence length. Key vulnerability: P Simran Singh's SR drops 9% under pressure -- opposition will target this window."
        },
        "RR": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "Sandeep Sharma",
                        "dotSequences": 10,
                        "avgLength": 2.7,
                        "maxLength": 4
                    },
                    {
                        "name": "RA Jadeja",
                        "dotSequences": 12,
                        "avgLength": 2.6,
                        "maxLength": 4
                    },
                    {
                        "name": "TU Deshpande",
                        "dotSequences": 14,
                        "avgLength": 2.6,
                        "maxLength": 4
                    }
                ],
                "teamTotalSequences": 59,
                "bestMaxStreak": 4
            },
            "battingResilience": {
                "rating": "Limited",
                "topBatters": [
                    {
                        "name": "YBK Jaiswal",
                        "boundarySequences": 9,
                        "avgLength": 2.4,
                        "maxLength": 4
                    },
                    {
                        "name": "Dhruv Jurel",
                        "boundarySequences": 7,
                        "avgLength": 2.4,
                        "maxLength": 3
                    },
                    {
                        "name": "SO Hetmyer",
                        "boundarySequences": 4,
                        "avgLength": 2.3,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 31,
                "bestMaxStreak": 4
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "RA Jadeja",
                        "normalSR": 149.3,
                        "pressureSR": 159.4,
                        "delta": "+6.8"
                    },
                    {
                        "name": "R Parag",
                        "normalSR": 156.5,
                        "pressureSR": 163.4,
                        "delta": "+4.4"
                    },
                    {
                        "name": "Dhruv Jurel",
                        "normalSR": 157.6,
                        "pressureSR": 159.3,
                        "delta": "+1.1"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "YBK Jaiswal",
                        "normalSR": 160.0,
                        "pressureSR": 148.2,
                        "delta": "-7.4"
                    },
                    {
                        "name": "SO Hetmyer",
                        "normalSR": 156.0,
                        "pressureSR": 149.8,
                        "delta": "-4.0"
                    }
                ],
                "teamAvgDelta": 0.3
            },
            "andyFlowerInsight": "RR lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.7. Counter-attack capability is limited -- YBK Jaiswal leads with just 2.4 avg boundary sequence length. Key vulnerability: YBK Jaiswal's SR drops 7% under pressure -- opposition will target this window."
        },
        "SRH": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "E Malinga",
                        "dotSequences": 4,
                        "avgLength": 2.8,
                        "maxLength": 4
                    },
                    {
                        "name": "HV Patel",
                        "dotSequences": 7,
                        "avgLength": 2.7,
                        "maxLength": 4
                    },
                    {
                        "name": "PJ Cummins",
                        "dotSequences": 12,
                        "avgLength": 2.4,
                        "maxLength": 4
                    }
                ],
                "teamTotalSequences": 38,
                "bestMaxStreak": 4
            },
            "battingResilience": {
                "rating": "Average",
                "topBatters": [
                    {
                        "name": "Ishan Kishan",
                        "boundarySequences": 8,
                        "avgLength": 2.5,
                        "maxLength": 3
                    },
                    {
                        "name": "H Klaasen",
                        "boundarySequences": 4,
                        "avgLength": 2.5,
                        "maxLength": 4
                    },
                    {
                        "name": "TM Head",
                        "boundarySequences": 2,
                        "avgLength": 2.5,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 33,
                "bestMaxStreak": 4
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "H Klaasen",
                        "normalSR": 161.0,
                        "pressureSR": 162.3,
                        "delta": "+0.8"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "Nithish Kumar Reddy",
                        "normalSR": 136.8,
                        "pressureSR": 108.3,
                        "delta": "-20.8"
                    },
                    {
                        "name": "TM Head",
                        "normalSR": 178.7,
                        "pressureSR": 153.8,
                        "delta": "-13.9"
                    },
                    {
                        "name": "Ishan Kishan",
                        "normalSR": 149.7,
                        "pressureSR": 134.5,
                        "delta": "-10.1"
                    }
                ],
                "teamAvgDelta": -8.2
            },
            "andyFlowerInsight": "SRH lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.8. Counter-attack capability is limited -- Ishan Kishan leads with just 2.5 avg boundary sequence length. Key vulnerability: Nithish Kumar Reddy's SR drops 21% under pressure -- opposition will target this window."
        },
        "GT": {
            "bowlingPressure": {
                "rating": "Weak",
                "topBowlers": [
                    {
                        "name": "I Sharma",
                        "dotSequences": 9,
                        "avgLength": 2.8,
                        "maxLength": 4
                    },
                    {
                        "name": "M Prasidh Krishna",
                        "dotSequences": 9,
                        "avgLength": 2.7,
                        "maxLength": 4
                    },
                    {
                        "name": "Mohammed Siraj",
                        "dotSequences": 25,
                        "avgLength": 2.5,
                        "maxLength": 5
                    }
                ],
                "teamTotalSequences": 55,
                "bestMaxStreak": 5
            },
            "battingResilience": {
                "rating": "Strong",
                "topBatters": [
                    {
                        "name": "JC Buttler",
                        "boundarySequences": 4,
                        "avgLength": 3.0,
                        "maxLength": 4
                    },
                    {
                        "name": "M Shahrukh Khan",
                        "boundarySequences": 2,
                        "avgLength": 2.5,
                        "maxLength": 3
                    },
                    {
                        "name": "Shubman Gill",
                        "boundarySequences": 6,
                        "avgLength": 2.2,
                        "maxLength": 3
                    }
                ],
                "teamTotalSequences": 27,
                "bestMaxStreak": 4
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "Shubman Gill",
                        "normalSR": 141.4,
                        "pressureSR": 164.1,
                        "delta": "+16.0"
                    },
                    {
                        "name": "B Sai Sudharsan",
                        "normalSR": 141.8,
                        "pressureSR": 147.4,
                        "delta": "+3.9"
                    },
                    {
                        "name": "JC Buttler",
                        "normalSR": 147.8,
                        "pressureSR": 152.6,
                        "delta": "+3.2"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "R Tewatia",
                        "normalSR": 133.8,
                        "pressureSR": 121.3,
                        "delta": "-9.3"
                    },
                    {
                        "name": "M Shahrukh Khan",
                        "normalSR": 173.3,
                        "pressureSR": 169.6,
                        "delta": "-2.1"
                    },
                    {
                        "name": "Washington Sundar",
                        "normalSR": 167.9,
                        "pressureSR": 167.3,
                        "delta": "-0.4"
                    }
                ],
                "teamAvgDelta": 1.9
            },
            "andyFlowerInsight": "GT lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 2.8. Counter-attack capability led by JC Buttler (4 consecutive boundaries under pressure). Key vulnerability: R Tewatia's SR drops 9% under pressure -- opposition will target this window."
        },
        "LSG": {
            "bowlingPressure": {
                "rating": "Average",
                "topBowlers": [
                    {
                        "name": "M Siddharth",
                        "dotSequences": 3,
                        "avgLength": 3.0,
                        "maxLength": 4
                    },
                    {
                        "name": "Mohammed Shami",
                        "dotSequences": 17,
                        "avgLength": 2.8,
                        "maxLength": 5
                    },
                    {
                        "name": "Akash Singh",
                        "dotSequences": 10,
                        "avgLength": 2.8,
                        "maxLength": 5
                    }
                ],
                "teamTotalSequences": 62,
                "bestMaxStreak": 5
            },
            "battingResilience": {
                "rating": "Strong",
                "topBatters": [
                    {
                        "name": "RR Pant",
                        "boundarySequences": 3,
                        "avgLength": 3.3,
                        "maxLength": 6
                    },
                    {
                        "name": "N Pooran",
                        "boundarySequences": 12,
                        "avgLength": 2.4,
                        "maxLength": 3
                    },
                    {
                        "name": "AK Markram",
                        "boundarySequences": 2,
                        "avgLength": 2.0,
                        "maxLength": 2
                    }
                ],
                "teamTotalSequences": 21,
                "bestMaxStreak": 6
            },
            "clutchPerformers": {
                "topClutch": [
                    {
                        "name": "A Badoni",
                        "normalSR": 129.0,
                        "pressureSR": 135.2,
                        "delta": "+4.8"
                    },
                    {
                        "name": "RR Pant",
                        "normalSR": 138.9,
                        "pressureSR": 144.3,
                        "delta": "+3.9"
                    },
                    {
                        "name": "N Pooran",
                        "normalSR": 195.4,
                        "pressureSR": 200.6,
                        "delta": "+2.6"
                    }
                ],
                "chokeRisks": [
                    {
                        "name": "JP Inglis",
                        "normalSR": 156.0,
                        "pressureSR": 133.3,
                        "delta": "-14.5"
                    },
                    {
                        "name": "AK Markram",
                        "normalSR": 130.1,
                        "pressureSR": 111.6,
                        "delta": "-14.2"
                    },
                    {
                        "name": "MR Marsh",
                        "normalSR": 137.8,
                        "pressureSR": 122.6,
                        "delta": "-11.0"
                    }
                ],
                "teamAvgDelta": -5.5
            },
            "andyFlowerInsight": "LSG lacks a sustained dot-ball pressure weapon -- longest avg sequence is just 3.0. Counter-attack capability led by RR Pant (6 consecutive boundaries under pressure). Key vulnerability: JP Inglis's SR drops 14% under pressure -- opposition will target this window."
        }
    }
};
