/**
 * The Lab - Player Rankings Data (Dual-Scope)
 * IPL Pre-Season Analytics (EPIC-021 Signature Feature)
 * Auto-generated: 2026-02-15T09:38:45Z
 * Generator: scripts/generators/generate_rankings.py (TKT-236)
 *
 * Categories per scope: 7
 * Scopes: alltime (2008-2025), since2023 (2023-2025)
 * Composite methodology: see config/thresholds.yaml > rankings
 */

const RANKINGS_DATA = {
  "alltime": {
    "categories": [
      {
        "id": "batter_phase",
        "title": "Batter Phase Rankings",
        "description": "Phase-specific batter composites. Combines SR percentile (40%), Avg percentile (40%), and Boundary% percentile (20%). Sample-size weighted (target: 200 balls per phase).",
        "subcategories": [
          {
            "id": "powerplay",
            "title": "Powerplay (Overs 1-6)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "TM Head",
                365,
                184.4,
                44.9,
                34.0,
                92.8
              ],
              [
                2,
                "JM Bairstow",
                623,
                151.5,
                49.7,
                25.5,
                91.4
              ],
              [
                3,
                "YBK Jaiswal",
                864,
                159.5,
                44.5,
                29.2,
                89.6
              ],
              [
                4,
                "CA Lynn",
                537,
                145.1,
                48.7,
                25.3,
                87.9
              ],
              [
                5,
                "SA Yadav",
                667,
                140.3,
                58.5,
                23.8,
                87.0
              ],
              [
                6,
                "PD Salt",
                409,
                176.5,
                38.0,
                31.3,
                86.5
              ],
              [
                7,
                "RD Rickelton",
                193,
                153.9,
                42.4,
                26.4,
                83.1
              ],
              [
                8,
                "Abhishek Sharma",
                629,
                161.8,
                36.4,
                27.2,
                82.4
              ],
              [
                9,
                "B Sai Sudharsan",
                489,
                137.8,
                112.3,
                20.6,
                82.3
              ],
              [
                10,
                "DA Warner",
                2385,
                139.0,
                46.7,
                22.5,
                81.4
              ],
              [
                11,
                "MR Marsh",
                347,
                149.3,
                39.9,
                23.3,
                80.3
              ],
              [
                12,
                "JC Buttler",
                1199,
                140.7,
                43.3,
                23.5,
                79.4
              ],
              [
                13,
                "KP Pietersen",
                293,
                133.8,
                78.4,
                20.1,
                79.2
              ],
              [
                14,
                "F du Plessis",
                1670,
                136.6,
                43.9,
                21.7,
                75.9
              ],
              [
                14,
                "P Simran Singh",
                583,
                149.6,
                33.5,
                25.0,
                75.9
              ],
              [
                16,
                "Priyansh Arya",
                217,
                177.0,
                29.5,
                30.9,
                75.8
              ],
              [
                17,
                "Ishan Kishan",
                997,
                134.1,
                44.6,
                22.1,
                75.6
              ],
              [
                18,
                "ML Hayden",
                456,
                131.4,
                46.1,
                22.1,
                75.2
              ],
              [
                19,
                "Abishek Porel",
                208,
                151.9,
                31.6,
                24.5,
                74.9
              ],
              [
                20,
                "E Lewis",
                286,
                146.8,
                32.3,
                24.5,
                73.2
              ]
            ],
            "qualifiedCount": 133
          },
          {
            "id": "middle",
            "title": "Middle Overs (7-15)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "H Klaasen",
                526,
                159.3,
                59.9,
                18.6,
                95.7
              ],
              [
                2,
                "DP Conway",
                341,
                152.8,
                65.1,
                19.4,
                95.4
              ],
              [
                3,
                "N Pooran",
                764,
                167.0,
                44.0,
                23.3,
                94.1
              ],
              [
                4,
                "CH Gayle",
                1285,
                156.5,
                44.7,
                20.7,
                93.2
              ],
              [
                4,
                "SE Marsh",
                971,
                149.1,
                51.7,
                19.6,
                93.2
              ],
              [
                6,
                "JC Buttler",
                1180,
                144.4,
                43.7,
                17.7,
                86.8
              ],
              [
                7,
                "RM Patidar",
                480,
                162.5,
                37.1,
                19.2,
                86.7
              ],
              [
                8,
                "B Sai Sudharsan",
                620,
                143.1,
                46.7,
                16.3,
                86.3
              ],
              [
                8,
                "N Wadhera",
                380,
                140.3,
                44.4,
                18.9,
                86.3
              ],
              [
                10,
                "AD Russell",
                767,
                154.1,
                34.8,
                22.8,
                86.1
              ],
              [
                11,
                "SA Yadav",
                1770,
                144.3,
                40.5,
                18.9,
                85.2
              ],
              [
                12,
                "V Sehwag",
                611,
                173.8,
                32.2,
                24.7,
                84.6
              ],
              [
                13,
                "Shubman Gill",
                1193,
                143.8,
                45.1,
                15.2,
                84.4
              ],
              [
                14,
                "SR Watson",
                1302,
                154.1,
                33.4,
                21.3,
                83.7
              ],
              [
                15,
                "Tilak Varma",
                703,
                136.4,
                48.0,
                15.9,
                82.9
              ],
              [
                16,
                "RD Gaikwad",
                732,
                142.5,
                43.5,
                15.4,
                82.4
              ],
              [
                17,
                "D Brevis",
                207,
                155.1,
                32.1,
                19.8,
                81.3
              ],
              [
                18,
                "VR Iyer",
                521,
                139.7,
                40.4,
                16.1,
                80.0
              ],
              [
                19,
                "RR Pant",
                1556,
                136.6,
                40.1,
                17.1,
                79.8
              ],
              [
                20,
                "JM Sharma",
                386,
                143.5,
                32.6,
                19.2,
                77.8
              ]
            ],
            "qualifiedCount": 195
          },
          {
            "id": "death",
            "title": "Death Overs (16-20)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "AB de Villiers",
                829,
                225.3,
                46.7,
                33.2,
                99.2
              ],
              [
                2,
                "T Stubbs",
                199,
                220.6,
                87.8,
                32.7,
                98.5
              ],
              [
                3,
                "CH Gayle",
                280,
                207.5,
                38.7,
                31.8,
                97.3
              ],
              [
                4,
                "Shashank Singh",
                219,
                193.6,
                42.4,
                26.5,
                93.0
              ],
              [
                5,
                "JC Buttler",
                368,
                198.1,
                33.1,
                27.7,
                91.7
              ],
              [
                6,
                "H Klaasen",
                277,
                199.6,
                29.1,
                27.4,
                89.0
              ],
              [
                7,
                "RK Singh",
                317,
                191.8,
                30.4,
                29.3,
                88.9
              ],
              [
                8,
                "TH David",
                351,
                192.6,
                30.7,
                27.1,
                88.8
              ],
              [
                9,
                "AD Russell",
                725,
                197.5,
                26.0,
                31.3,
                85.3
              ],
              [
                10,
                "CL White",
                192,
                189.1,
                36.3,
                23.4,
                83.0
              ],
              [
                11,
                "RR Pant",
                492,
                203.2,
                24.4,
                31.5,
                82.6
              ],
              [
                12,
                "SV Samson",
                407,
                191.7,
                26.0,
                26.8,
                81.2
              ],
              [
                12,
                "Dhruv Jurel",
                229,
                179.0,
                31.5,
                24.0,
                81.2
              ],
              [
                14,
                "MS Dhoni",
                1965,
                176.5,
                35.4,
                23.4,
                79.9
              ],
              [
                15,
                "SS Iyer",
                370,
                180.8,
                27.9,
                24.6,
                79.4
              ],
              [
                16,
                "KL Rahul",
                472,
                177.8,
                31.1,
                23.3,
                79.0
              ],
              [
                17,
                "Tilak Varma",
                212,
                183.5,
                25.9,
                25.5,
                77.9
              ],
              [
                18,
                "N Pooran",
                476,
                176.1,
                28.9,
                24.6,
                77.3
              ],
              [
                19,
                "MP Stoinis",
                481,
                178.2,
                27.6,
                24.5,
                77.1
              ],
              [
                20,
                "V Kohli",
                803,
                187.7,
                25.1,
                24.9,
                76.9
              ]
            ],
            "qualifiedCount": 165
          }
        ]
      },
      {
        "id": "bowler_phase",
        "title": "Bowler Phase Rankings",
        "description": "Phase-specific bowler composites. Combines Economy percentile (50%) and Dot Ball% percentile (50%). Sample-size weighted (target: 120 balls per phase).",
        "subcategories": [
          {
            "id": "powerplay",
            "title": "Powerplay (Overs 1-6)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "R Rampaul",
                156,
                5.85,
                58.3,
                97.9
              ],
              [
                2,
                "GD McGrath",
                222,
                5.89,
                57.2,
                97.3
              ],
              [
                3,
                "WPUJC Vaas",
                198,
                6.39,
                57.1,
                94.3
              ],
              [
                4,
                "Sohail Tanvir",
                132,
                6.59,
                57.6,
                94.1
              ],
              [
                5,
                "BW Hilfenhaus",
                240,
                6.5,
                55.4,
                93.3
              ],
              [
                6,
                "DW Steyn",
                1134,
                6.42,
                55.0,
                92.8
              ],
              [
                7,
                "JC Archer",
                546,
                6.62,
                56.0,
                92.4
              ],
              [
                8,
                "AC Thomas",
                180,
                6.53,
                54.4,
                91.6
              ],
              [
                9,
                "RJ Harris",
                426,
                6.76,
                55.4,
                91.0
              ],
              [
                10,
                "DP Nannes",
                342,
                6.61,
                53.8,
                90.8
              ],
              [
                11,
                "SM Pollock",
                204,
                6.26,
                51.5,
                90.4
              ],
              [
                12,
                "A Symonds",
                114,
                5.79,
                54.4,
                90.3
              ],
              [
                13,
                "B Kumar",
                2339,
                6.71,
                53.5,
                90.2
              ],
              [
                14,
                "SL Malinga",
                1111,
                6.53,
                52.4,
                90.1
              ],
              [
                15,
                "IC Pandey",
                264,
                7.09,
                57.2,
                89.5
              ],
              [
                16,
                "A Kumble",
                108,
                5.0,
                59.3,
                89.3
              ],
              [
                17,
                "M Muralitharan",
                144,
                6.29,
                50.7,
                88.7
              ],
              [
                18,
                "JJ Bumrah",
                1122,
                6.87,
                51.7,
                86.7
              ],
              [
                19,
                "IK Pathan",
                918,
                7.22,
                55.2,
                85.4
              ],
              [
                19,
                "KW Richardson",
                168,
                7.0,
                51.8,
                85.4
              ]
            ],
            "qualifiedCount": 244
          },
          {
            "id": "middle",
            "title": "Middle Overs (7-15)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "MM Patel",
                396,
                6.17,
                39.4,
                97.6
              ],
              [
                2,
                "Azhar Mahmood",
                186,
                6.61,
                40.9,
                96.6
              ],
              [
                3,
                "DW Steyn",
                408,
                6.75,
                43.4,
                96.1
              ],
              [
                4,
                "Shivam Mavi",
                162,
                6.85,
                43.8,
                95.6
              ],
              [
                5,
                "JJ Bumrah",
                870,
                6.66,
                39.7,
                95.4
              ],
              [
                6,
                "J Yadav",
                210,
                6.29,
                38.1,
                94.8
              ],
              [
                7,
                "NM Coulter-Nile",
                249,
                6.89,
                41.0,
                94.3
              ],
              [
                8,
                "M Muralitharan",
                1105,
                6.65,
                38.2,
                94.0
              ],
              [
                9,
                "MF Maharoof",
                150,
                6.6,
                38.0,
                93.7
              ],
              [
                9,
                "CR Woakes",
                120,
                6.75,
                38.3,
                93.7
              ],
              [
                11,
                "RE van der Merwe",
                312,
                6.19,
                37.2,
                93.4
              ],
              [
                12,
                "AB Dinda",
                294,
                6.65,
                38.1,
                93.2
              ],
              [
                13,
                "R Sharma",
                684,
                6.75,
                37.0,
                90.6
              ],
              [
                14,
                "J Botha",
                396,
                6.44,
                35.9,
                89.6
              ],
              [
                15,
                "B Akhil",
                132,
                6.41,
                35.6,
                89.1
              ],
              [
                16,
                "A Kumble",
                690,
                6.8,
                36.5,
                88.8
              ],
              [
                17,
                "P Awana",
                306,
                7.25,
                38.6,
                88.6
              ],
              [
                18,
                "SK Warne",
                942,
                6.87,
                36.6,
                88.3
              ],
              [
                19,
                "JC Archer",
                216,
                7.44,
                42.6,
                87.5
              ],
              [
                19,
                "WD Parnell",
                120,
                7.05,
                36.7,
                87.5
              ]
            ],
            "qualifiedCount": 308
          },
          {
            "id": "death",
            "title": "Death Overs (16-20)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "DE Bollinger",
                234,
                7.62,
                37.6,
                98.3
              ],
              [
                2,
                "SP Narine",
                1051,
                7.5,
                36.4,
                97.2
              ],
              [
                3,
                "M Muralitharan",
                275,
                8.29,
                37.5,
                95.2
              ],
              [
                4,
                "A Kumble",
                167,
                7.8,
                34.7,
                95.0
              ],
              [
                5,
                "Noor Ahmad",
                127,
                8.41,
                42.5,
                94.7
              ],
              [
                6,
                "Harmeet Singh",
                129,
                8.28,
                35.7,
                93.9
              ],
              [
                7,
                "PWH de Silva",
                120,
                8.5,
                37.5,
                93.0
              ],
              [
                8,
                "KH Pandya",
                202,
                8.32,
                35.1,
                92.9
              ],
              [
                9,
                "CV Varun",
                304,
                8.55,
                36.2,
                91.4
              ],
              [
                10,
                "DW Steyn",
                634,
                8.47,
                34.4,
                90.2
              ],
              [
                11,
                "RD Chahar",
                164,
                8.16,
                32.9,
                89.9
              ],
              [
                12,
                "Rashid Khan",
                576,
                8.56,
                34.7,
                89.7
              ],
              [
                13,
                "Harbhajan Singh",
                273,
                8.4,
                33.3,
                88.2
              ],
              [
                14,
                "SW Tait",
                150,
                8.64,
                33.3,
                86.7
              ],
              [
                15,
                "PP Chawla",
                444,
                8.88,
                33.8,
                86.6
              ],
              [
                16,
                "SL Malinga",
                1117,
                8.2,
                31.3,
                85.9
              ],
              [
                17,
                "Kuldeep Yadav",
                334,
                8.39,
                31.7,
                85.4
              ],
              [
                18,
                "WD Parnell",
                231,
                8.75,
                32.9,
                84.6
              ],
              [
                19,
                "JJ Bumrah",
                1345,
                8.4,
                31.4,
                84.4
              ],
              [
                20,
                "Sohail Tanvir",
                103,
                7.11,
                36.9,
                83.9
              ]
            ],
            "qualifiedCount": 199
          }
        ]
      },
      {
        "id": "batter_vs_bowling_type",
        "title": "Batter vs Bowling Type",
        "description": "How batters perform against each bowling classification. Composite: SR (40%) + Avg (40%) + Survival Rate (20%). Min 50 balls. Sample-size weighted (target: 100 balls).",
        "subcategories": [
          {
            "id": "right_arm_pace",
            "title": "vs Right-arm pace",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "SO Hetmyer",
                131,
                214.5,
                93.7,
                98.6
              ],
              [
                2,
                "JM Bairstow",
                123,
                180.5,
                111.0,
                97.7
              ],
              [
                3,
                "MP Stoinis",
                253,
                163.6,
                46.0,
                90.2
              ],
              [
                4,
                "AB de Villiers",
                999,
                161.3,
                46.0,
                89.3
              ],
              [
                5,
                "HM Amla",
                146,
                159.6,
                46.6,
                89.1
              ],
              [
                6,
                "VR Iyer",
                116,
                156.0,
                45.2,
                87.2
              ],
              [
                7,
                "ML Hayden",
                333,
                144.4,
                80.2,
                87.1
              ],
              [
                8,
                "AK Markram",
                96,
                158.3,
                50.7,
                87.1
              ],
              [
                9,
                "MS Dhoni",
                1170,
                156.4,
                43.6,
                86.4
              ],
              [
                10,
                "SM Katich",
                101,
                147.5,
                49.7,
                86.2
              ],
              [
                11,
                "Q de Kock",
                509,
                151.7,
                42.9,
                84.3
              ],
              [
                12,
                "RN ten Doeschate",
                104,
                143.3,
                49.7,
                84.2
              ],
              [
                13,
                "JP Duminy",
                517,
                143.5,
                49.5,
                84.0
              ],
              [
                14,
                "CA Lynn",
                220,
                165.9,
                36.5,
                82.6
              ],
              [
                15,
                "SR Watson",
                971,
                153.3,
                40.2,
                82.5
              ],
              [
                16,
                "RA Tripathi",
                248,
                162.1,
                36.5,
                82.2
              ],
              [
                17,
                "F du Plessis",
                679,
                142.6,
                44.0,
                81.3
              ],
              [
                18,
                "SV Samson",
                766,
                152.6,
                39.0,
                81.0
              ],
              [
                19,
                "GJ Bailey",
                218,
                147.7,
                40.2,
                80.5
              ],
              [
                20,
                "JC Buttler",
                426,
                164.3,
                35.0,
                80.0
              ]
            ],
            "qualifiedCount": 231
          },
          {
            "id": "fast",
            "title": "vs Fast",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "LS Livingstone",
                131,
                206.1,
                54.0,
                91.5
              ],
              [
                2,
                "C Green",
                128,
                171.9,
                55.0,
                88.9
              ],
              [
                3,
                "RA Jadeja",
                363,
                159.8,
                64.4,
                87.8
              ],
              [
                4,
                "A Badoni",
                203,
                168.0,
                42.6,
                83.7
              ],
              [
                5,
                "KD Karthik",
                458,
                162.9,
                43.9,
                83.4
              ],
              [
                6,
                "JC Buttler",
                618,
                147.4,
                56.9,
                80.6
              ],
              [
                7,
                "RD Gaikwad",
                425,
                145.9,
                62.0,
                80.0
              ],
              [
                8,
                "JP Inglis",
                81,
                195.1,
                158.0,
                79.9
              ],
              [
                9,
                "PD Salt",
                162,
                176.5,
                35.8,
                79.9
              ],
              [
                10,
                "AB de Villiers",
                360,
                170.8,
                36.2,
                78.7
              ],
              [
                11,
                "Abishek Porel",
                154,
                154.6,
                39.7,
                76.6
              ],
              [
                12,
                "CH Gayle",
                353,
                144.2,
                50.9,
                75.5
              ],
              [
                13,
                "B Sai Sudharsan",
                384,
                142.7,
                54.8,
                75.3
              ],
              [
                14,
                "Abdul Samad",
                144,
                182.6,
                32.9,
                75.2
              ],
              [
                15,
                "KL Rahul",
                848,
                137.6,
                72.9,
                74.9
              ],
              [
                16,
                "PJ Cummins",
                112,
                174.1,
                32.5,
                74.2
              ],
              [
                17,
                "AD Russell",
                368,
                186.1,
                32.6,
                73.8
              ],
              [
                18,
                "DA Miller",
                321,
                144.6,
                42.2,
                73.2
              ],
              [
                18,
                "MS Dhoni",
                430,
                152.6,
                36.4,
                73.2
              ],
              [
                20,
                "R Tewatia",
                231,
                154.1,
                35.6,
                72.6
              ]
            ],
            "qualifiedCount": 142
          },
          {
            "id": "fast_medium",
            "title": "vs Fast-Medium",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "RK Singh",
                107,
                176.6,
                189.0,
                95.1
              ],
              [
                2,
                "AB de Villiers",
                195,
                181.5,
                70.8,
                94.4
              ],
              [
                3,
                "TH David",
                133,
                178.2,
                59.2,
                91.9
              ],
              [
                4,
                "Priyansh Arya",
                102,
                201.0,
                51.2,
                90.6
              ],
              [
                5,
                "CH Gayle",
                169,
                166.3,
                46.8,
                86.7
              ],
              [
                6,
                "JM Bairstow",
                295,
                156.9,
                51.4,
                83.8
              ],
              [
                7,
                "PD Salt",
                207,
                179.7,
                41.3,
                82.9
              ],
              [
                8,
                "JM Sharma",
                132,
                162.9,
                43.0,
                82.5
              ],
              [
                9,
                "MM Ali",
                171,
                147.9,
                50.6,
                79.4
              ],
              [
                10,
                "MR Marsh",
                201,
                160.2,
                40.2,
                78.6
              ],
              [
                11,
                "MP Stoinis",
                205,
                164.4,
                37.4,
                76.7
              ],
              [
                11,
                "DA Warner",
                486,
                146.7,
                44.6,
                76.7
              ],
              [
                13,
                "TM Head",
                161,
                180.8,
                36.4,
                76.3
              ],
              [
                14,
                "JC Buttler",
                544,
                153.7,
                38.0,
                73.0
              ],
              [
                15,
                "MS Dhoni",
                293,
                162.1,
                36.5,
                72.9
              ],
              [
                15,
                "Dhruv Jurel",
                112,
                183.9,
                34.3,
                72.9
              ],
              [
                17,
                "KL Rahul",
                651,
                146.2,
                38.1,
                70.3
              ],
              [
                18,
                "DP Conway",
                197,
                136.0,
                53.6,
                69.8
              ],
              [
                18,
                "YBK Jaiswal",
                386,
                167.1,
                34.0,
                69.8
              ],
              [
                20,
                "Tilak Varma",
                231,
                155.8,
                36.0,
                69.4
              ]
            ],
            "qualifiedCount": 127
          },
          {
            "id": "left_arm_pace",
            "title": "vs Left-arm pace",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "Ishan Kishan",
                140,
                167.1,
                117.0,
                94.8
              ],
              [
                2,
                "Shubman Gill",
                137,
                157.7,
                216.0,
                93.6
              ],
              [
                3,
                "KP Pietersen",
                110,
                168.2,
                61.7,
                92.7
              ],
              [
                4,
                "CH Gayle",
                316,
                155.4,
                49.1,
                84.5
              ],
              [
                5,
                "SA Yadav",
                161,
                179.5,
                41.3,
                83.6
              ],
              [
                6,
                "AB de Villiers",
                291,
                160.8,
                42.5,
                81.1
              ],
              [
                7,
                "KH Pandya",
                119,
                152.1,
                45.2,
                80.5
              ],
              [
                8,
                "DJ Hussey",
                108,
                138.0,
                74.5,
                80.4
              ],
              [
                9,
                "RR Pant",
                96,
                170.8,
                41.0,
                79.6
              ],
              [
                10,
                "LMP Simmons",
                131,
                131.3,
                172.0,
                77.7
              ],
              [
                11,
                "DA Miller",
                139,
                132.4,
                61.3,
                75.5
              ],
              [
                12,
                "MC Henriques",
                79,
                162.0,
                null,
                75.4
              ],
              [
                13,
                "PP Shaw",
                87,
                164.4,
                47.7,
                75.1
              ],
              [
                14,
                "CA Lynn",
                76,
                168.4,
                128.0,
                73.3
              ],
              [
                15,
                "AM Rahane",
                411,
                131.9,
                49.3,
                72.5
              ],
              [
                16,
                "GJ Maxwell",
                125,
                161.6,
                33.7,
                70.7
              ],
              [
                17,
                "KA Pollard",
                200,
                154.0,
                34.2,
                69.6
              ],
              [
                18,
                "KL Rahul",
                281,
                130.2,
                45.8,
                69.3
              ],
              [
                19,
                "KM Jadhav",
                88,
                137.5,
                60.5,
                68.8
              ],
              [
                20,
                "MK Pandey",
                254,
                126.8,
                53.7,
                68.8
              ]
            ],
            "qualifiedCount": 113
          },
          {
            "id": "right_arm_off_spin",
            "title": "vs Right-arm off-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "SA Yadav",
                222,
                140.1,
                103.7,
                84.4
              ],
              [
                2,
                "Shubman Gill",
                172,
                148.3,
                63.8,
                82.7
              ],
              [
                3,
                "AB de Villiers",
                285,
                143.9,
                68.3,
                82.4
              ],
              [
                3,
                "SR Watson",
                163,
                171.2,
                55.8,
                82.4
              ],
              [
                5,
                "SS Iyer",
                179,
                131.3,
                117.5,
                82.1
              ],
              [
                6,
                "AD Mathews",
                127,
                128.3,
                163.0,
                81.4
              ],
              [
                7,
                "Tilak Varma",
                102,
                126.5,
                129.0,
                79.4
              ],
              [
                7,
                "SE Marsh",
                249,
                141.8,
                58.8,
                79.4
              ],
              [
                9,
                "KS Williamson",
                139,
                125.2,
                null,
                79.0
              ],
              [
                10,
                "DJ Bravo",
                127,
                135.4,
                57.3,
                75.9
              ],
              [
                11,
                "KL Rahul",
                185,
                140.5,
                52.0,
                75.1
              ],
              [
                12,
                "DA Warner",
                540,
                128.7,
                69.5,
                74.6
              ],
              [
                13,
                "HH Pandya",
                82,
                150.0,
                123.0,
                74.3
              ],
              [
                14,
                "N Rana",
                210,
                159.1,
                41.8,
                71.4
              ],
              [
                14,
                "KD Karthik",
                321,
                140.8,
                45.2,
                71.4
              ],
              [
                16,
                "JC Buttler",
                166,
                153.6,
                42.5,
                71.3
              ],
              [
                17,
                "MEK Hussey",
                240,
                121.2,
                72.8,
                68.3
              ],
              [
                17,
                "S Badrinath",
                145,
                124.1,
                60.0,
                68.3
              ],
              [
                19,
                "SV Samson",
                155,
                129.0,
                50.0,
                67.9
              ],
              [
                20,
                "JM Bairstow",
                77,
                145.4,
                112.0,
                67.8
              ]
            ],
            "qualifiedCount": 127
          },
          {
            "id": "right_arm_leg_spin",
            "title": "vs Right-arm leg-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "SE Marsh",
                112,
                167.9,
                62.7,
                91.8
              ],
              [
                2,
                "CH Gayle",
                248,
                191.1,
                59.2,
                90.3
              ],
              [
                3,
                "DA Warner",
                272,
                145.2,
                56.4,
                86.1
              ],
              [
                4,
                "DPMD Jayawardene",
                99,
                137.4,
                136.0,
                85.8
              ],
              [
                5,
                "V Sehwag",
                158,
                174.1,
                45.8,
                83.4
              ],
              [
                6,
                "DA Miller",
                199,
                135.7,
                54.0,
                81.1
              ],
              [
                7,
                "V Kohli",
                485,
                136.1,
                50.8,
                79.2
              ],
              [
                8,
                "MEK Hussey",
                90,
                138.9,
                62.5,
                77.9
              ],
              [
                9,
                "RR Pant",
                96,
                145.8,
                46.7,
                77.6
              ],
              [
                10,
                "YK Pathan",
                216,
                147.2,
                39.8,
                77.3
              ],
              [
                11,
                "KA Pollard",
                236,
                149.6,
                39.2,
                76.8
              ],
              [
                12,
                "JA Morkel",
                77,
                180.5,
                139.0,
                74.8
              ],
              [
                13,
                "JM Bairstow",
                82,
                151.2,
                62.0,
                74.5
              ],
              [
                14,
                "KP Pietersen",
                93,
                145.2,
                45.0,
                73.0
              ],
              [
                15,
                "A Symonds",
                119,
                147.1,
                35.0,
                71.8
              ],
              [
                16,
                "G Gambhir",
                219,
                128.8,
                47.0,
                71.6
              ],
              [
                17,
                "S Dhawan",
                265,
                141.5,
                34.1,
                69.5
              ],
              [
                18,
                "SK Raina",
                462,
                134.2,
                38.8,
                68.8
              ],
              [
                19,
                "KK Nair",
                105,
                150.5,
                31.6,
                68.0
              ],
              [
                20,
                "SC Ganguly",
                130,
                118.5,
                51.3,
                66.3
              ]
            ],
            "qualifiedCount": 96
          },
          {
            "id": "leg_spin",
            "title": "vs Leg-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "RM Patidar",
                108,
                214.8,
                58.0,
                89.5
              ],
              [
                2,
                "N Wadhera",
                118,
                155.9,
                61.3,
                89.0
              ],
              [
                3,
                "H Klaasen",
                95,
                177.9,
                56.3,
                85.3
              ],
              [
                4,
                "N Pooran",
                143,
                172.7,
                49.4,
                84.1
              ],
              [
                5,
                "SA Yadav",
                376,
                146.5,
                61.2,
                83.7
              ],
              [
                6,
                "S Dube",
                144,
                160.4,
                46.2,
                81.0
              ],
              [
                7,
                "DA Warner",
                201,
                149.8,
                50.2,
                80.2
              ],
              [
                8,
                "RR Pant",
                326,
                144.2,
                52.2,
                77.6
              ],
              [
                9,
                "Tilak Varma",
                167,
                144.3,
                48.2,
                74.9
              ],
              [
                10,
                "CH Gayle",
                116,
                145.7,
                42.2,
                71.0
              ],
              [
                11,
                "B Sai Sudharsan",
                105,
                149.5,
                39.2,
                69.5
              ],
              [
                12,
                "Shubman Gill",
                291,
                140.9,
                45.6,
                69.3
              ],
              [
                13,
                "YBK Jaiswal",
                110,
                133.6,
                49.0,
                68.5
              ],
              [
                14,
                "KL Rahul",
                328,
                118.6,
                55.6,
                64.6
              ],
              [
                15,
                "A Raghuvanshi",
                67,
                167.2,
                112.0,
                64.1
              ],
              [
                16,
                "D Padikkal",
                187,
                126.7,
                47.4,
                63.9
              ],
              [
                17,
                "SR Watson",
                123,
                135.0,
                41.5,
                63.2
              ],
              [
                18,
                "AR Patel",
                179,
                147.5,
                33.0,
                62.4
              ],
              [
                19,
                "Abhishek Sharma",
                87,
                210.3,
                36.6,
                61.8
              ],
              [
                20,
                "SPD Smith",
                118,
                98.3,
                116.0,
                61.2
              ]
            ],
            "qualifiedCount": 83
          },
          {
            "id": "off_spin",
            "title": "vs Off-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "HH Pandya",
                101,
                134.7,
                136.0,
                86.2
              ],
              [
                2,
                "H Klaasen",
                88,
                181.8,
                160.0,
                85.3
              ],
              [
                3,
                "JC Buttler",
                123,
                140.7,
                57.7,
                77.2
              ],
              [
                4,
                "DA Warner",
                255,
                147.8,
                53.9,
                75.9
              ],
              [
                5,
                "RA Tripathi",
                113,
                136.3,
                51.3,
                72.1
              ],
              [
                6,
                "KL Rahul",
                223,
                123.3,
                68.8,
                70.3
              ],
              [
                7,
                "SA Yadav",
                140,
                119.3,
                83.5,
                69.7
              ],
              [
                8,
                "Shubman Gill",
                91,
                165.9,
                50.3,
                69.3
              ],
              [
                9,
                "MK Pandey",
                119,
                110.9,
                132.0,
                69.3
              ],
              [
                10,
                "AK Markram",
                111,
                133.3,
                49.3,
                67.2
              ],
              [
                11,
                "S Dube",
                131,
                116.8,
                76.5,
                64.1
              ],
              [
                12,
                "RD Gaikwad",
                139,
                119.4,
                55.3,
                62.4
              ],
              [
                13,
                "YBK Jaiswal",
                66,
                189.4,
                125.0,
                62.1
              ],
              [
                14,
                "N Pooran",
                126,
                161.1,
                33.8,
                61.7
              ],
              [
                15,
                "V Kohli",
                238,
                120.6,
                47.8,
                59.7
              ],
              [
                16,
                "DA Miller",
                74,
                125.7,
                93.0,
                58.2
              ],
              [
                17,
                "JM Bairstow",
                63,
                158.7,
                100.0,
                56.7
              ],
              [
                18,
                "Abhishek Sharma",
                67,
                189.6,
                63.5,
                55.9
              ],
              [
                19,
                "CH Gayle",
                116,
                118.1,
                45.7,
                55.2
              ],
              [
                20,
                "SV Samson",
                136,
                120.6,
                41.0,
                54.8
              ]
            ],
            "qualifiedCount": 59
          },
          {
            "id": "la_orthodox",
            "title": "vs LA Orthodox",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "B Sai Sudharsan",
                121,
                167.8,
                101.5,
                89.5
              ],
              [
                2,
                "RD Gaikwad",
                116,
                146.6,
                170.0,
                87.7
              ],
              [
                3,
                "Ishan Kishan",
                143,
                144.8,
                103.5,
                83.1
              ],
              [
                3,
                "S Dhawan",
                163,
                133.7,
                218.0,
                83.1
              ],
              [
                5,
                "N Pooran",
                83,
                245.8,
                204.0,
                80.0
              ],
              [
                6,
                "Tilak Varma",
                97,
                138.1,
                134.0,
                79.8
              ],
              [
                7,
                "DA Warner",
                164,
                162.2,
                66.5,
                79.7
              ],
              [
                8,
                "RM Patidar",
                96,
                156.2,
                75.0,
                79.5
              ],
              [
                9,
                "Shubman Gill",
                261,
                130.3,
                170.0,
                78.2
              ],
              [
                10,
                "AD Russell",
                102,
                146.1,
                74.5,
                77.9
              ],
              [
                11,
                "JC Buttler",
                186,
                136.0,
                84.3,
                76.9
              ],
              [
                12,
                "Q de Kock",
                100,
                146.0,
                73.0,
                76.4
              ],
              [
                13,
                "AR Patel",
                77,
                171.4,
                null,
                74.8
              ],
              [
                14,
                "G Gambhir",
                89,
                134.8,
                120.0,
                71.6
              ],
              [
                15,
                "N Rana",
                132,
                147.7,
                48.8,
                70.8
              ],
              [
                16,
                "F du Plessis",
                302,
                130.8,
                65.8,
                67.4
              ],
              [
                17,
                "D Padikkal",
                119,
                147.1,
                43.8,
                65.6
              ],
              [
                18,
                "SS Iyer",
                225,
                118.2,
                66.5,
                62.1
              ],
              [
                18,
                "RR Pant",
                123,
                153.7,
                37.8,
                62.1
              ],
              [
                20,
                "SK Raina",
                87,
                140.2,
                61.0,
                61.6
              ]
            ],
            "qualifiedCount": 79
          },
          {
            "id": "left_arm_orthodox",
            "title": "vs Left-arm orthodox",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "DA Warner",
                142,
                158.4,
                112.5,
                94.9
              ],
              [
                2,
                "SPD Smith",
                122,
                150.0,
                91.5,
                87.9
              ],
              [
                3,
                "AB de Villiers",
                268,
                151.5,
                81.2,
                87.7
              ],
              [
                4,
                "CH Gayle",
                98,
                205.1,
                67.0,
                86.1
              ],
              [
                5,
                "F du Plessis",
                215,
                138.1,
                74.2,
                81.3
              ],
              [
                6,
                "BJ Hodge",
                185,
                120.0,
                111.0,
                77.2
              ],
              [
                6,
                "SV Samson",
                180,
                158.9,
                40.9,
                77.2
              ],
              [
                8,
                "GJ Maxwell",
                82,
                175.6,
                72.0,
                73.4
              ],
              [
                9,
                "G Gambhir",
                264,
                139.8,
                41.0,
                71.5
              ],
              [
                10,
                "SE Marsh",
                87,
                162.1,
                47.0,
                70.9
              ],
              [
                11,
                "V Kohli",
                376,
                118.3,
                74.2,
                70.0
              ],
              [
                12,
                "JC Buttler",
                81,
                190.1,
                51.3,
                67.9
              ],
              [
                13,
                "Yuvraj Singh",
                117,
                153.8,
                36.0,
                66.9
              ],
              [
                14,
                "AM Rahane",
                323,
                122.9,
                49.6,
                66.4
              ],
              [
                15,
                "KA Pollard",
                153,
                142.5,
                36.3,
                66.2
              ],
              [
                16,
                "M Vijay",
                224,
                117.4,
                65.8,
                65.6
              ],
              [
                17,
                "DA Miller",
                80,
                130.0,
                104.0,
                65.2
              ],
              [
                18,
                "RA Jadeja",
                131,
                136.6,
                35.8,
                63.1
              ],
              [
                19,
                "CL White",
                88,
                127.3,
                56.0,
                62.5
              ],
              [
                20,
                "YK Pathan",
                180,
                171.1,
                30.8,
                60.5
              ]
            ],
            "qualifiedCount": 79
          },
          {
            "id": "medium",
            "title": "vs Medium",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "V Kohli",
                113,
                157.5,
                178.0,
                94.4
              ],
              [
                2,
                "YK Pathan",
                81,
                165.4,
                134.0,
                75.4
              ],
              [
                3,
                "S Dhawan",
                145,
                135.9,
                65.7,
                66.3
              ],
              [
                4,
                "SE Marsh",
                82,
                120.7,
                99.0,
                57.4
              ],
              [
                5,
                "MS Dhoni",
                78,
                124.4,
                97.0,
                55.6
              ],
              [
                6,
                "GJ Maxwell",
                58,
                232.8,
                135.0,
                53.3
              ],
              [
                7,
                "AB de Villiers",
                109,
                128.4,
                35.0,
                52.5
              ],
              [
                8,
                "SA Yadav",
                62,
                141.9,
                88.0,
                50.4
              ],
              [
                9,
                "SS Iyer",
                60,
                140.0,
                84.0,
                46.9
              ],
              [
                10,
                "BJ Hodge",
                54,
                124.1,
                null,
                42.6
              ],
              [
                11,
                "WP Saha",
                70,
                128.6,
                45.0,
                40.7
              ],
              [
                12,
                "BB McCullum",
                73,
                157.5,
                28.8,
                40.2
              ],
              [
                13,
                "SPD Smith",
                75,
                124.0,
                46.5,
                39.8
              ],
              [
                14,
                "RG Sharma",
                58,
                127.6,
                74.0,
                38.0
              ],
              [
                15,
                "DA Warner",
                98,
                118.4,
                29.0,
                36.8
              ],
              [
                16,
                "DR Smith",
                88,
                137.5,
                24.2,
                35.7
              ],
              [
                17,
                "SK Raina",
                152,
                114.5,
                29.0,
                35.6
              ],
              [
                18,
                "DA Miller",
                60,
                136.7,
                41.0,
                35.3
              ],
              [
                19,
                "SV Samson",
                53,
                128.3,
                68.0,
                34.5
              ],
              [
                20,
                "RV Uthappa",
                83,
                144.6,
                24.0,
                33.7
              ]
            ],
            "qualifiedCount": 33
          },
          {
            "id": "wrist_spin",
            "title": "vs Wrist-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "V Kohli",
                111,
                131.5,
                48.7,
                65.0
              ],
              [
                2,
                "R Parag",
                57,
                145.6,
                83.0,
                54.2
              ],
              [
                3,
                "SA Yadav",
                73,
                141.1,
                34.3,
                38.3
              ],
              [
                4,
                "JC Buttler",
                61,
                141.0,
                43.0,
                38.1
              ],
              [
                5,
                "SS Iyer",
                64,
                150.0,
                32.0,
                35.2
              ],
              [
                6,
                "RG Sharma",
                52,
                128.8,
                67.0,
                29.9
              ],
              [
                7,
                "DA Warner",
                53,
                130.2,
                34.5,
                23.9
              ],
              [
                8,
                "SV Samson",
                57,
                129.8,
                24.7,
                8.5
              ],
              [
                9,
                "RR Pant",
                58,
                87.9,
                17.0,
                1.5
              ]
            ],
            "qualifiedCount": 9
          }
        ]
      },
      {
        "id": "bowler_vs_handedness",
        "title": "Bowler vs Batter Handedness",
        "description": "Bowler effectiveness against left-hand and right-hand batters. Composite: Economy percentile (50%) + SR percentile (50%). Min 50 balls. Sample-size weighted (target: 100 balls).",
        "subcategories": [
          {
            "id": "left_hand",
            "title": "vs Left-Hand Batters",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Wkts",
              "Econ",
              "Composite"
            ],
            "rows": [
              [
                1,
                "M Prasidh Krishna",
                107,
                9,
                6.84,
                96.2
              ],
              [
                1,
                "JJ Bumrah",
                210,
                17,
                5.94,
                96.2
              ],
              [
                3,
                "Noor Ahmad",
                219,
                18,
                7.89,
                92.4
              ],
              [
                4,
                "RD Chahar",
                127,
                8,
                6.94,
                87.5
              ],
              [
                5,
                "M Pathirana",
                213,
                21,
                8.99,
                81.5
              ],
              [
                6,
                "VG Arora",
                167,
                13,
                8.95,
                78.3
              ],
              [
                6,
                "DL Chahar",
                184,
                11,
                8.25,
                78.3
              ],
              [
                6,
                "Rashid Khan",
                317,
                19,
                8.27,
                78.3
              ],
              [
                9,
                "JR Hazlewood",
                104,
                11,
                9.29,
                77.2
              ],
              [
                10,
                "TA Boult",
                285,
                17,
                8.46,
                76.1
              ],
              [
                11,
                "SP Narine",
                232,
                12,
                7.55,
                75.0
              ],
              [
                12,
                "MM Ali",
                119,
                6,
                6.45,
                74.5
              ],
              [
                13,
                "PP Chawla",
                161,
                9,
                8.68,
                70.1
              ],
              [
                14,
                "Sandeep Sharma",
                252,
                13,
                8.38,
                69.0
              ],
              [
                15,
                "Ravi Bishnoi",
                268,
                14,
                8.78,
                66.8
              ],
              [
                16,
                "WG Jacks",
                93,
                7,
                9.29,
                66.7
              ],
              [
                17,
                "Mukesh Kumar",
                227,
                18,
                9.81,
                65.8
              ],
              [
                18,
                "Arshdeep Singh",
                301,
                24,
                9.87,
                65.2
              ],
              [
                19,
                "Kuldeep Yadav",
                317,
                15,
                8.08,
                64.1
              ],
              [
                20,
                "GJ Maxwell",
                136,
                7,
                8.87,
                63.6
              ]
            ],
            "qualifiedCount": 93
          },
          {
            "id": "right_hand",
            "title": "vs Right-Hand Batters",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Wkts",
              "Econ",
              "Composite"
            ],
            "rows": [
              [
                1,
                "TA Boult",
                388,
                28,
                8.46,
                87.2
              ],
              [
                2,
                "PP Chawla",
                233,
                16,
                8.65,
                84.4
              ],
              [
                3,
                "JJ Bumrah",
                305,
                18,
                7.18,
                83.5
              ],
              [
                4,
                "E Malinga",
                123,
                11,
                9.17,
                82.6
              ],
              [
                5,
                "M Prasidh Krishna",
                218,
                16,
                9.03,
                81.2
              ],
              [
                6,
                "CV Varun",
                498,
                30,
                7.86,
                80.7
              ],
              [
                7,
                "M Markande",
                159,
                10,
                8.79,
                78.0
              ],
              [
                8,
                "R Sai Kishore",
                246,
                16,
                8.95,
                77.5
              ],
              [
                9,
                "Mustafizur Rahman",
                161,
                12,
                9.35,
                77.1
              ],
              [
                9,
                "JR Hazlewood",
                192,
                12,
                8.72,
                77.1
              ],
              [
                11,
                "JD Unadkat",
                199,
                12,
                8.68,
                76.1
              ],
              [
                12,
                "YS Chahal",
                448,
                26,
                8.37,
                75.2
              ],
              [
                13,
                "RA Jadeja",
                422,
                21,
                7.28,
                74.8
              ],
              [
                14,
                "B Kumar",
                415,
                26,
                9.22,
                71.1
              ],
              [
                15,
                "HV Patel",
                439,
                31,
                9.62,
                70.2
              ],
              [
                16,
                "Mohammed Siraj",
                424,
                24,
                8.82,
                69.3
              ],
              [
                17,
                "M Pathirana",
                340,
                22,
                9.41,
                68.8
              ],
              [
                18,
                "Kuldeep Yadav",
                406,
                19,
                7.98,
                67.4
              ],
              [
                19,
                "MJ Santner",
                239,
                11,
                7.76,
                67.0
              ],
              [
                20,
                "Sandeep Sharma",
                318,
                21,
                9.64,
                66.5
              ]
            ],
            "qualifiedCount": 110
          }
        ]
      },
      {
        "id": "player_matchups",
        "title": "Player Matchup Rankings",
        "description": "Head-to-head dominance index. Positive = batter-favored, negative = bowler-favored. Factors: SR deviation (50%), Avg deviation (30%), Boundary% deviation (20%). Min 12 balls. Sample-size weighted (target: 50 balls).",
        "subcategories": [
          {
            "id": "batter_favored",
            "title": "Batter-Favored Matchups",
            "description": "Matchups where the batter dominates (high SR, high avg, low dismissal rate)",
            "headers": [
              "Rank",
              "Batter",
              "Bowler",
              "Balls",
              "Runs",
              "Outs",
              "SR",
              "Dominance"
            ],
            "rows": [
              [
                1,
                "RR Pant",
                "B Kumar",
                54,
                120,
                1,
                222.2,
                79.0
              ],
              [
                2,
                "MS Dhoni",
                "JD Unadkat",
                44,
                106,
                1,
                240.9,
                73.5
              ],
              [
                3,
                "KL Rahul",
                "Mohammed Siraj",
                79,
                135,
                1,
                170.9,
                56.3
              ],
              [
                4,
                "JC Buttler",
                "Sandeep Sharma",
                48,
                91,
                1,
                189.6,
                49.9
              ],
              [
                5,
                "Abhishek Sharma",
                "Rashid Khan",
                36,
                82,
                1,
                227.8,
                49.8
              ],
              [
                6,
                "H Klaasen",
                "CV Varun",
                35,
                77,
                1,
                220.0,
                44.7
              ],
              [
                7,
                "KL Rahul",
                "HH Pandya",
                55,
                96,
                1,
                174.6,
                44.6
              ],
              [
                8,
                "YBK Jaiswal",
                "JR Hazlewood",
                32,
                81,
                3,
                253.1,
                44.3
              ],
              [
                9,
                "SV Samson",
                "Mohammed Shami",
                43,
                82,
                1,
                190.7,
                44.2
              ],
              [
                10,
                "SV Samson",
                "Arshdeep Singh",
                42,
                79,
                1,
                188.1,
                40.7
              ],
              [
                11,
                "KL Rahul",
                "YS Chahal",
                83,
                125,
                1,
                150.6,
                40.7
              ],
              [
                12,
                "KL Rahul",
                "JR Hazlewood",
                50,
                85,
                1,
                170.0,
                39.8
              ],
              [
                13,
                "SA Yadav",
                "Mohammed Siraj",
                29,
                67,
                1,
                231.0,
                39.3
              ],
              [
                14,
                "V Kohli",
                "I Sharma",
                75,
                112,
                1,
                149.3,
                37.3
              ],
              [
                15,
                "N Wadhera",
                "PWH de Silva",
                36,
                72,
                1,
                200.0,
                36.8
              ],
              [
                16,
                "RA Jadeja",
                "HV Patel",
                37,
                72,
                1,
                194.6,
                36.1
              ],
              [
                17,
                "SS Iyer",
                "SM Curran",
                37,
                72,
                1,
                194.6,
                36.1
              ],
              [
                18,
                "SV Samson",
                "KK Ahmed",
                54,
                87,
                1,
                161.1,
                36.0
              ],
              [
                19,
                "MP Stoinis",
                "M Prasidh Krishna",
                16,
                50,
                1,
                312.5,
                34.2
              ],
              [
                20,
                "Abhishek Sharma",
                "I Sharma",
                30,
                63,
                1,
                210.0,
                34.2
              ]
            ],
            "qualifiedCount": 1761
          },
          {
            "id": "bowler_favored",
            "title": "Bowler-Favored Matchups",
            "description": "Matchups where the bowler dominates (low SR, frequent dismissals)",
            "headers": [
              "Rank",
              "Batter",
              "Bowler",
              "Balls",
              "Runs",
              "Outs",
              "SR",
              "Dominance"
            ],
            "rows": [
              [
                1,
                "MS Dhoni",
                "SP Narine",
                77,
                40,
                2,
                52.0,
                -43.3
              ],
              [
                2,
                "JC Buttler",
                "Rashid Khan",
                50,
                30,
                4,
                60.0,
                -43.2
              ],
              [
                3,
                "MK Pandey",
                "AR Patel",
                67,
                43,
                2,
                64.2,
                -36.4
              ],
              [
                4,
                "MS Dhoni",
                "RD Chahar",
                34,
                19,
                2,
                55.9,
                -30.0
              ],
              [
                5,
                "SV Samson",
                "SP Narine",
                81,
                65,
                3,
                80.2,
                -27.9
              ],
              [
                6,
                "S Dube",
                "JJ Bumrah",
                35,
                23,
                3,
                65.7,
                -27.4
              ],
              [
                7,
                "SS Iyer",
                "Sandeep Sharma",
                56,
                47,
                3,
                83.9,
                -27.1
              ],
              [
                8,
                "AR Patel",
                "CV Varun",
                28,
                14,
                2,
                50.0,
                -26.7
              ],
              [
                9,
                "MK Pandey",
                "YS Chahal",
                60,
                53,
                4,
                88.3,
                -26.0
              ],
              [
                10,
                "MS Dhoni",
                "HV Patel",
                35,
                25,
                4,
                71.4,
                -25.7
              ],
              [
                11,
                "MK Pandey",
                "I Sharma",
                44,
                31,
                1,
                70.5,
                -25.7
              ],
              [
                12,
                "MK Pandey",
                "RA Jadeja",
                53,
                45,
                2,
                84.9,
                -25.5
              ],
              [
                13,
                "HH Pandya",
                "Rashid Khan",
                38,
                28,
                2,
                73.7,
                -25.4
              ],
              [
                14,
                "AM Rahane",
                "Mohammed Siraj",
                32,
                19,
                1,
                59.4,
                -25.3
              ],
              [
                15,
                "RG Sharma",
                "KK Ahmed",
                49,
                42,
                3,
                85.7,
                -24.7
              ],
              [
                16,
                "RA Jadeja",
                "Rashid Khan",
                35,
                23,
                1,
                65.7,
                -24.6
              ],
              [
                17,
                "RG Sharma",
                "Sandeep Sharma",
                44,
                38,
                5,
                86.4,
                -24.4
              ],
              [
                18,
                "SS Iyer",
                "B Kumar",
                50,
                45,
                3,
                90.0,
                -24.4
              ],
              [
                19,
                "KL Rahul",
                "AR Patel",
                39,
                30,
                2,
                76.9,
                -24.2
              ],
              [
                20,
                "MP Stoinis",
                "JJ Bumrah",
                38,
                30,
                3,
                79.0,
                -23.9
              ]
            ],
            "qualifiedCount": 1761
          }
        ]
      },
      {
        "id": "batter_composite",
        "title": "Overall Batter Rankings",
        "description": "Composite score: Career SR+Avg (30%) + Phase Performance (30%) + Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). Sample-size weighted. Min 500 balls.",
        "subcategories": [
          {
            "id": "overall",
            "title": "Overall Batter Rankings",
            "description": "Composite score: Career SR+Avg (30%) + Phase Performance (30%) + Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). Sample-size weighted. Min 500 balls.",
            "headers": [
              "Rank",
              "Player",
              "Inn",
              "Runs",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Raw Score",
              "Weighted"
            ],
            "rows": [
              [
                1,
                "H Klaasen",
                45,
                1480,
                863,
                171.5,
                41.1,
                21.7,
                93.4,
                93.4
              ],
              [
                2,
                "B Sai Sudharsan",
                40,
                1793,
                1221,
                146.8,
                51.2,
                19.3,
                87.0,
                87.0
              ],
              [
                3,
                "TM Head",
                37,
                1146,
                667,
                171.8,
                35.8,
                27.1,
                86.1,
                86.1
              ],
              [
                4,
                "N Pooran",
                86,
                2293,
                1353,
                169.5,
                35.8,
                24.0,
                85.5,
                85.5
              ],
              [
                5,
                "AB de Villiers",
                170,
                5162,
                3392,
                152.2,
                42.3,
                19.6,
                84.9,
                84.9
              ],
              [
                6,
                "JC Buttler",
                119,
                4120,
                2747,
                150.0,
                41.2,
                21.6,
                84.8,
                84.8
              ],
              [
                7,
                "PD Salt",
                34,
                1056,
                595,
                177.5,
                34.1,
                29.9,
                81.7,
                81.7
              ],
              [
                8,
                "SA Yadav",
                151,
                4311,
                2888,
                149.3,
                36.2,
                21.5,
                81.6,
                81.6
              ],
              [
                9,
                "DP Conway",
                28,
                1080,
                770,
                140.3,
                45.0,
                19.6,
                81.6,
                81.6
              ],
              [
                10,
                "CH Gayle",
                141,
                4965,
                3318,
                149.6,
                40.0,
                23.0,
                80.1,
                80.1
              ],
              [
                11,
                "RM Patidar",
                38,
                1111,
                719,
                154.5,
                31.7,
                20.0,
                79.7,
                79.7
              ],
              [
                12,
                "Tilak Varma",
                51,
                1499,
                1032,
                145.2,
                39.5,
                18.1,
                78.9,
                78.9
              ],
              [
                13,
                "RR Pant",
                123,
                3553,
                2398,
                148.2,
                34.8,
                20.4,
                78.0,
                78.0
              ],
              [
                14,
                "DA Warner",
                184,
                6565,
                4677,
                140.4,
                42.1,
                19.2,
                77.4,
                77.4
              ],
              [
                15,
                "JM Bairstow",
                52,
                1674,
                1142,
                146.6,
                35.6,
                21.6,
                76.5,
                76.5
              ],
              [
                16,
                "AD Russell",
                114,
                2651,
                1506,
                176.0,
                29.8,
                27.2,
                76.2,
                76.2
              ],
              [
                17,
                "YBK Jaiswal",
                66,
                2166,
                1412,
                153.4,
                34.9,
                24.9,
                76.1,
                76.1
              ],
              [
                18,
                "RD Gaikwad",
                70,
                2502,
                1811,
                138.2,
                41.7,
                18.0,
                74.9,
                74.9
              ],
              [
                19,
                "KL Rahul",
                135,
                5222,
                3828,
                136.4,
                47.5,
                17.2,
                74.4,
                74.4
              ],
              [
                20,
                "Shubman Gill",
                114,
                3866,
                2774,
                139.4,
                40.7,
                17.7,
                74.1,
                74.1
              ]
            ],
            "qualifiedCount": 128
          }
        ]
      },
      {
        "id": "bowler_composite",
        "title": "Overall Bowler Rankings",
        "description": "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) + Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). Sample-size weighted. Min 300 balls.",
        "subcategories": [
          {
            "id": "overall",
            "title": "Overall Bowler Rankings",
            "description": "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) + Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). Sample-size weighted. Min 300 balls.",
            "headers": [
              "Rank",
              "Player",
              "Matches",
              "Balls",
              "Wkts",
              "Econ",
              "Avg",
              "Bowl SR",
              "Raw Score",
              "Weighted"
            ],
            "rows": [
              [
                1,
                "DE Bollinger",
                27,
                576,
                37,
                7.46,
                19.4,
                15.6,
                90.2,
                90.2
              ],
              [
                2,
                "SL Malinga",
                122,
                2828,
                170,
                7.4,
                20.5,
                16.6,
                88.7,
                88.7
              ],
              [
                3,
                "AD Mascarenhas",
                13,
                308,
                19,
                7.11,
                19.2,
                16.2,
                88.4,
                88.4
              ],
              [
                4,
                "A Kumble",
                42,
                965,
                45,
                6.77,
                24.2,
                21.4,
                88.1,
                88.1
              ],
              [
                5,
                "JJ Bumrah",
                145,
                3337,
                183,
                7.43,
                22.6,
                18.2,
                88.1,
                88.1
              ],
              [
                6,
                "DW Steyn",
                95,
                2176,
                97,
                7.08,
                26.5,
                22.4,
                86.7,
                86.7
              ],
              [
                7,
                "MF Maharoof",
                20,
                420,
                27,
                7.6,
                19.7,
                15.6,
                82.7,
                82.7
              ],
              [
                8,
                "M Muralitharan",
                66,
                1524,
                63,
                6.91,
                27.9,
                24.2,
                82.3,
                82.3
              ],
              [
                9,
                "SP Narine",
                187,
                4345,
                192,
                6.93,
                26.1,
                22.6,
                81.7,
                81.7
              ],
              [
                10,
                "MM Patel",
                63,
                1355,
                74,
                7.67,
                23.4,
                18.3,
                81.5,
                81.5
              ],
              [
                11,
                "NM Coulter-Nile",
                38,
                857,
                48,
                7.88,
                23.4,
                17.9,
                81.3,
                81.3
              ],
              [
                12,
                "SK Warne",
                54,
                1194,
                57,
                7.36,
                25.7,
                20.9,
                80.0,
                80.0
              ],
              [
                13,
                "RJ Harris",
                37,
                832,
                45,
                7.82,
                24.1,
                18.5,
                79.6,
                79.6
              ],
              [
                14,
                "A Mishra",
                162,
                3371,
                174,
                7.46,
                24.1,
                19.4,
                78.4,
                78.4
              ],
              [
                15,
                "Rashid Khan",
                136,
                3189,
                158,
                7.23,
                24.3,
                20.2,
                78.1,
                78.1
              ],
              [
                16,
                "MM Ali",
                57,
                854,
                41,
                7.28,
                25.3,
                20.8,
                78.0,
                78.0
              ],
              [
                17,
                "Harbhajan Singh",
                160,
                3416,
                150,
                7.2,
                27.3,
                22.8,
                77.7,
                77.7
              ],
              [
                18,
                "A Nehra",
                88,
                1908,
                106,
                7.98,
                23.9,
                18.0,
                76.5,
                76.5
              ],
              [
                19,
                "BW Hilfenhaus",
                17,
                372,
                22,
                8.02,
                22.6,
                16.9,
                76.0,
                76.0
              ],
              [
                20,
                "RE van der Merwe",
                21,
                443,
                21,
                6.98,
                24.5,
                21.1,
                75.8,
                75.8
              ]
            ],
            "qualifiedCount": 199
          }
        ]
      }
    ],
    "stats": {
      "batter_phase": 493,
      "bowler_phase": 751,
      "batter_vs_bowling_type": 1178,
      "bowler_vs_handedness": 203,
      "player_matchups": 1761,
      "batter_composite": 128,
      "bowler_composite": 199
    }
  },
  "since2023": {
    "categories": [
      {
        "id": "batter_phase",
        "title": "Batter Phase Rankings",
        "description": "Phase-specific batter composites. Combines SR percentile (40%), Avg percentile (40%), and Boundary% percentile (20%). Sample-size weighted (target: 200 balls per phase).",
        "subcategories": [
          {
            "id": "powerplay",
            "title": "Powerplay (Overs 1-6)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "TM Head",
                348,
                190.5,
                51.0,
                35.3,
                89.3
              ],
              [
                2,
                "AM Rahane",
                301,
                168.8,
                72.6,
                27.9,
                88.8
              ],
              [
                3,
                "YBK Jaiswal",
                595,
                170.1,
                53.3,
                31.9,
                86.1
              ],
              [
                4,
                "PD Salt",
                409,
                176.5,
                38.0,
                31.3,
                76.3
              ],
              [
                5,
                "Abhishek Sharma",
                404,
                178.2,
                34.3,
                30.2,
                72.6
              ],
              [
                6,
                "V Kohli",
                653,
                151.9,
                90.2,
                23.4,
                72.1
              ],
              [
                7,
                "SP Narine",
                290,
                167.2,
                37.3,
                30.0,
                70.2
              ],
              [
                8,
                "F du Plessis",
                516,
                155.2,
                44.5,
                25.8,
                68.4
              ],
              [
                9,
                "RD Rickelton",
                193,
                153.9,
                42.4,
                26.4,
                65.5
              ],
              [
                10,
                "Priyansh Arya",
                217,
                177.0,
                29.5,
                30.9,
                63.7
              ],
              [
                11,
                "MR Marsh",
                262,
                153.8,
                40.3,
                24.8,
                62.8
              ],
              [
                12,
                "RD Gaikwad",
                462,
                145.9,
                61.3,
                22.3,
                61.9
              ],
              [
                13,
                "P Simran Singh",
                541,
                153.1,
                37.6,
                25.9,
                61.4
              ],
              [
                14,
                "DA Warner",
                292,
                145.2,
                47.1,
                26.7,
                60.9
              ],
              [
                15,
                "SV Samson",
                265,
                143.8,
                54.4,
                24.9,
                60.5
              ],
              [
                16,
                "JM Bairstow",
                155,
                160.7,
                49.8,
                26.4,
                58.7
              ],
              [
                17,
                "B Sai Sudharsan",
                463,
                139.5,
                129.2,
                20.9,
                55.4
              ],
              [
                18,
                "Shubman Gill",
                579,
                143.7,
                55.5,
                21.8,
                54.9
              ],
              [
                19,
                "Ishan Kishan",
                448,
                146.9,
                36.6,
                24.6,
                50.2
              ],
              [
                20,
                "J Fraser-McGurk",
                142,
                209.9,
                29.8,
                40.1,
                49.2
              ]
            ],
            "qualifiedCount": 44
          },
          {
            "id": "middle",
            "title": "Middle Overs (7-15)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "N Pooran",
                390,
                183.8,
                59.8,
                27.2,
                96.0
              ],
              [
                2,
                "SA Yadav",
                685,
                173.0,
                59.2,
                25.7,
                93.1
              ],
              [
                3,
                "H Klaasen",
                514,
                161.5,
                63.9,
                19.1,
                89.1
              ],
              [
                4,
                "SS Iyer",
                353,
                154.4,
                90.8,
                19.3,
                86.6
              ],
              [
                5,
                "Shubman Gill",
                568,
                160.2,
                60.7,
                17.8,
                84.0
              ],
              [
                6,
                "JC Buttler",
                384,
                150.3,
                52.5,
                19.3,
                81.1
              ],
              [
                7,
                "DP Conway",
                259,
                146.3,
                63.2,
                17.4,
                79.4
              ],
              [
                8,
                "RM Patidar",
                318,
                168.2,
                35.7,
                21.1,
                78.9
              ],
              [
                9,
                "VR Iyer",
                355,
                145.9,
                51.8,
                16.6,
                73.4
              ],
              [
                10,
                "B Sai Sudharsan",
                550,
                145.8,
                47.2,
                16.7,
                72.6
              ],
              [
                11,
                "MR Marsh",
                236,
                158.1,
                31.1,
                22.0,
                70.0
              ],
              [
                12,
                "Abhishek Sharma",
                193,
                199.0,
                25.6,
                29.0,
                67.3
              ],
              [
                13,
                "N Wadhera",
                380,
                140.3,
                44.4,
                18.9,
                66.8
              ],
              [
                13,
                "R Parag",
                457,
                144.6,
                44.1,
                16.6,
                66.8
              ],
              [
                15,
                "JM Sharma",
                285,
                141.8,
                36.7,
                18.6,
                63.4
              ],
              [
                16,
                "S Dube",
                531,
                140.5,
                41.4,
                16.6,
                61.4
              ],
              [
                16,
                "Tilak Varma",
                489,
                138.8,
                45.3,
                16.8,
                61.4
              ],
              [
                18,
                "SV Samson",
                440,
                147.5,
                30.9,
                16.8,
                60.0
              ],
              [
                19,
                "F du Plessis",
                349,
                144.1,
                38.7,
                14.0,
                58.5
              ],
              [
                20,
                "RD Gaikwad",
                370,
                140.8,
                40.1,
                14.6,
                58.3
              ]
            ],
            "qualifiedCount": 71
          },
          {
            "id": "death",
            "title": "Death Overs (16-20)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "T Stubbs",
                197,
                221.8,
                87.4,
                33.0,
                93.7
              ],
              [
                2,
                "Shashank Singh",
                187,
                201.6,
                53.9,
                27.8,
                76.9
              ],
              [
                3,
                "RK Singh",
                241,
                197.1,
                31.7,
                30.3,
                76.2
              ],
              [
                4,
                "H Klaasen",
                246,
                206.5,
                29.9,
                28.9,
                72.5
              ],
              [
                5,
                "N Pooran",
                282,
                184.0,
                34.6,
                27.3,
                64.9
              ],
              [
                6,
                "SS Iyer",
                134,
                218.7,
                36.6,
                32.8,
                59.8
              ],
              [
                7,
                "AD Russell",
                194,
                194.3,
                23.6,
                32.0,
                56.6
              ],
              [
                8,
                "TH David",
                286,
                184.6,
                31.1,
                25.5,
                55.2
              ],
              [
                9,
                "MP Stoinis",
                121,
                228.1,
                34.5,
                34.7,
                54.6
              ],
              [
                10,
                "MS Dhoni",
                241,
                183.0,
                31.5,
                26.1,
                53.5
              ],
              [
                11,
                "LS Livingstone",
                100,
                234.0,
                39.0,
                36.0,
                47.9
              ],
              [
                12,
                "JC Buttler",
                133,
                191.0,
                42.3,
                27.1,
                47.5
              ],
              [
                13,
                "Dhruv Jurel",
                229,
                179.0,
                31.5,
                24.0,
                47.0
              ],
              [
                14,
                "Naman Dhir",
                121,
                204.1,
                30.9,
                31.4,
                45.5
              ],
              [
                15,
                "C Green",
                102,
                200.0,
                102.0,
                27.4,
                42.2
              ],
              [
                16,
                "SA Yadav",
                128,
                213.3,
                22.8,
                35.9,
                42.2
              ],
              [
                17,
                "Tilak Varma",
                151,
                192.7,
                26.4,
                27.1,
                42.1
              ],
              [
                18,
                "KD Karthik",
                189,
                188.4,
                22.2,
                28.6,
                40.4
              ],
              [
                19,
                "Ashutosh Sharma",
                143,
                190.2,
                27.2,
                26.6,
                37.5
              ],
              [
                20,
                "JM Sharma",
                178,
                191.6,
                20.1,
                28.1,
                37.0
              ]
            ],
            "qualifiedCount": 38
          }
        ]
      },
      {
        "id": "bowler_phase",
        "title": "Bowler Phase Rankings",
        "description": "Phase-specific bowler composites. Combines Economy percentile (50%) and Dot Ball% percentile (50%). Sample-size weighted (target: 120 balls per phase).",
        "subcategories": [
          {
            "id": "powerplay",
            "title": "Powerplay (Overs 1-6)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "JJ Bumrah",
                216,
                6.97,
                55.1,
                100.0
              ],
              [
                2,
                "JR Hazlewood",
                168,
                7.54,
                54.2,
                97.2
              ],
              [
                3,
                "TA Boult",
                564,
                7.55,
                50.4,
                95.7
              ],
              [
                4,
                "Mohammed Siraj",
                588,
                8.35,
                50.0,
                88.5
              ],
              [
                5,
                "B Kumar",
                594,
                8.26,
                47.5,
                87.0
              ],
              [
                6,
                "Mohammed Shami",
                396,
                8.67,
                49.0,
                82.7
              ],
              [
                7,
                "KK Ahmed",
                516,
                8.76,
                49.2,
                81.9
              ],
              [
                8,
                "JC Archer",
                204,
                8.53,
                45.1,
                74.7
              ],
              [
                9,
                "UT Yadav",
                186,
                8.84,
                46.2,
                73.9
              ],
              [
                10,
                "DL Chahar",
                482,
                8.53,
                44.4,
                71.8
              ],
              [
                11,
                "TU Deshpande",
                408,
                8.76,
                43.9,
                67.4
              ],
              [
                12,
                "Sandeep Sharma",
                312,
                7.58,
                40.7,
                65.3
              ],
              [
                13,
                "I Sharma",
                258,
                9.3,
                46.1,
                64.5
              ],
              [
                13,
                "JP Behrendorff",
                162,
                7.93,
                40.7,
                64.5
              ],
              [
                15,
                "CV Varun",
                186,
                8.19,
                40.9,
                63.1
              ],
              [
                16,
                "WD Parnell",
                102,
                8.35,
                44.1,
                62.9
              ],
              [
                17,
                "Akash Singh",
                133,
                9.25,
                44.4,
                58.7
              ],
              [
                18,
                "Akash Madhwal",
                78,
                8.08,
                47.4,
                57.0
              ],
              [
                19,
                "Arshdeep Singh",
                486,
                9.3,
                43.8,
                55.1
              ],
              [
                19,
                "Mustafizur Rahman",
                121,
                8.53,
                40.5,
                55.1
              ]
            ],
            "qualifiedCount": 70
          },
          {
            "id": "middle",
            "title": "Middle Overs (7-15)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "JJ Bumrah",
                180,
                6.17,
                43.9,
                99.5
              ],
              [
                2,
                "M Prasidh Krishna",
                168,
                6.82,
                40.5,
                97.5
              ],
              [
                3,
                "PJ Cummins",
                216,
                7.72,
                37.5,
                89.3
              ],
              [
                4,
                "MJ Santner",
                270,
                7.18,
                33.0,
                88.8
              ],
              [
                5,
                "CV Varun",
                565,
                8.01,
                37.2,
                85.7
              ],
              [
                6,
                "Harpreet Brar",
                378,
                7.44,
                32.3,
                84.7
              ],
              [
                7,
                "SP Narine",
                702,
                7.36,
                31.3,
                81.1
              ],
              [
                8,
                "Yash Dayal",
                157,
                8.14,
                33.1,
                79.1
              ],
              [
                9,
                "M Pathirana",
                276,
                8.35,
                35.1,
                78.1
              ],
              [
                10,
                "C Green",
                246,
                8.24,
                33.3,
                77.6
              ],
              [
                11,
                "GJ Maxwell",
                144,
                8.29,
                33.3,
                76.5
              ],
              [
                12,
                "AR Patel",
                540,
                7.48,
                30.6,
                76.0
              ],
              [
                13,
                "KH Pandya",
                492,
                7.45,
                30.3,
                75.0
              ],
              [
                13,
                "DS Rathi",
                162,
                7.74,
                30.9,
                75.0
              ],
              [
                15,
                "Noor Ahmad",
                611,
                8.18,
                32.2,
                74.5
              ],
              [
                15,
                "Kuldeep Yadav",
                708,
                7.72,
                30.8,
                74.5
              ],
              [
                17,
                "RA Jadeja",
                811,
                7.79,
                30.6,
                73.0
              ],
              [
                18,
                "RD Chahar",
                414,
                8.06,
                31.4,
                72.4
              ],
              [
                19,
                "J Little",
                96,
                8.06,
                36.5,
                66.6
              ],
              [
                20,
                "Naveen-ul-Haq",
                84,
                7.43,
                38.1,
                66.4
              ]
            ],
            "qualifiedCount": 99
          },
          {
            "id": "death",
            "title": "Death Overs (16-20)",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Econ",
              "Dot%",
              "Composite"
            ],
            "rows": [
              [
                1,
                "Noor Ahmad",
                127,
                8.41,
                42.5,
                97.4
              ],
              [
                2,
                "CV Varun",
                166,
                8.6,
                38.5,
                95.7
              ],
              [
                2,
                "JJ Bumrah",
                199,
                6.84,
                35.7,
                95.7
              ],
              [
                4,
                "Kuldeep Yadav",
                156,
                7.81,
                31.4,
                86.3
              ],
              [
                5,
                "M Pathirana",
                385,
                9.46,
                31.9,
                86.2
              ],
              [
                6,
                "Harshit Rana",
                157,
                9.82,
                33.8,
                84.5
              ],
              [
                7,
                "Mohammed Siraj",
                252,
                10.05,
                34.9,
                82.8
              ],
              [
                8,
                "Naveen-ul-Haq",
                160,
                9.98,
                29.4,
                73.3
              ],
              [
                9,
                "SP Narine",
                102,
                7.47,
                31.4,
                73.3
              ],
              [
                10,
                "M Prasidh Krishna",
                108,
                10.39,
                35.2,
                72.2
              ],
              [
                11,
                "YS Chahal",
                198,
                10.12,
                29.3,
                70.7
              ],
              [
                12,
                "Arshdeep Singh",
                315,
                10.5,
                31.1,
                69.0
              ],
              [
                13,
                "VG Arora",
                123,
                10.59,
                31.7,
                68.9
              ],
              [
                14,
                "AD Russell",
                149,
                10.71,
                32.2,
                68.1
              ],
              [
                15,
                "Ravi Bishnoi",
                109,
                10.79,
                35.8,
                65.0
              ],
              [
                16,
                "Rashid Khan",
                198,
                10.55,
                28.8,
                63.8
              ],
              [
                16,
                "TA Boult",
                180,
                10.17,
                28.3,
                63.8
              ],
              [
                18,
                "T Natarajan",
                254,
                10.13,
                27.9,
                63.0
              ],
              [
                19,
                "Mustafizur Rahman",
                128,
                10.78,
                31.2,
                62.1
              ],
              [
                20,
                "JR Hazlewood",
                89,
                10.65,
                36.0,
                56.3
              ]
            ],
            "qualifiedCount": 59
          }
        ]
      },
      {
        "id": "batter_vs_bowling_type",
        "title": "Batter vs Bowling Type",
        "description": "How batters perform against each bowling classification. Composite: SR (40%) + Avg (40%) + Survival Rate (20%). Min 50 balls. Sample-size weighted (target: 100 balls).",
        "subcategories": [
          {
            "id": "right_arm_pace",
            "title": "vs Right-arm pace",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "F du Plessis",
                80,
                187.5,
                150.0,
                72.0
              ],
              [
                2,
                "VR Iyer",
                72,
                194.4,
                70.0,
                61.9
              ],
              [
                3,
                "S Dube",
                104,
                139.4,
                72.5,
                58.0
              ],
              [
                4,
                "V Kohli",
                74,
                183.8,
                68.0,
                57.7
              ],
              [
                5,
                "Shashank Singh",
                54,
                194.4,
                null,
                51.8
              ],
              [
                6,
                "SA Yadav",
                74,
                218.9,
                40.5,
                47.9
              ],
              [
                7,
                "SV Samson",
                72,
                163.9,
                59.0,
                46.6
              ],
              [
                8,
                "RR Pant",
                57,
                201.8,
                57.5,
                46.3
              ],
              [
                9,
                "RD Gaikwad",
                87,
                183.9,
                40.0,
                45.8
              ],
              [
                10,
                "MP Stoinis",
                81,
                186.4,
                37.8,
                42.1
              ],
              [
                11,
                "RG Sharma",
                61,
                173.8,
                53.0,
                39.5
              ],
              [
                12,
                "YBK Jaiswal",
                83,
                160.2,
                44.3,
                39.3
              ],
              [
                13,
                "Shubman Gill",
                59,
                178.0,
                52.5,
                38.2
              ],
              [
                14,
                "N Pooran",
                67,
                179.1,
                40.0,
                33.5
              ],
              [
                15,
                "S Dhawan",
                51,
                149.0,
                76.0,
                32.6
              ],
              [
                16,
                "RK Singh",
                54,
                164.8,
                44.5,
                29.2
              ],
              [
                17,
                "KD Karthik",
                50,
                194.0,
                32.3,
                26.0
              ],
              [
                18,
                "DP Conway",
                62,
                140.3,
                43.5,
                24.8
              ],
              [
                19,
                "TH David",
                59,
                147.5,
                43.5,
                24.0
              ],
              [
                20,
                "R Parag",
                63,
                176.2,
                27.8,
                23.9
              ]
            ],
            "qualifiedCount": 31
          },
          {
            "id": "fast",
            "title": "vs Fast",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "N Rana",
                155,
                171.0,
                66.2,
                83.4
              ],
              [
                2,
                "AD Russell",
                123,
                200.0,
                41.0,
                80.2
              ],
              [
                3,
                "C Green",
                128,
                171.9,
                55.0,
                80.0
              ],
              [
                4,
                "RA Jadeja",
                141,
                157.4,
                111.0,
                78.9
              ],
              [
                5,
                "V Kohli",
                390,
                162.6,
                63.4,
                78.6
              ],
              [
                6,
                "JP Inglis",
                81,
                195.1,
                158.0,
                78.6
              ],
              [
                7,
                "A Badoni",
                167,
                172.5,
                41.1,
                74.5
              ],
              [
                8,
                "R Tewatia",
                112,
                161.6,
                45.2,
                71.7
              ],
              [
                9,
                "TM Head",
                164,
                177.4,
                36.4,
                71.0
              ],
              [
                10,
                "S Dhawan",
                130,
                148.5,
                64.3,
                70.6
              ],
              [
                11,
                "RR Pant",
                149,
                176.5,
                37.6,
                69.9
              ],
              [
                12,
                "SS Iyer",
                176,
                171.0,
                37.6,
                68.7
              ],
              [
                13,
                "LS Livingstone",
                70,
                220.0,
                154.0,
                68.5
              ],
              [
                14,
                "RG Sharma",
                233,
                163.9,
                38.2,
                68.3
              ],
              [
                15,
                "PD Salt",
                162,
                176.5,
                35.8,
                67.8
              ],
              [
                16,
                "JC Buttler",
                244,
                145.9,
                59.3,
                67.4
              ],
              [
                17,
                "SA Yadav",
                191,
                177.0,
                33.8,
                66.9
              ],
              [
                18,
                "B Sai Sudharsan",
                368,
                144.6,
                59.1,
                66.2
              ],
              [
                19,
                "KH Pandya",
                108,
                154.6,
                41.8,
                65.1
              ],
              [
                20,
                "RD Gaikwad",
                217,
                136.9,
                59.4,
                64.8
              ]
            ],
            "qualifiedCount": 88
          },
          {
            "id": "fast_medium",
            "title": "vs Fast-Medium",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "Priyansh Arya",
                102,
                201.0,
                51.2,
                88.0
              ],
              [
                2,
                "TH David",
                114,
                173.7,
                66.0,
                85.9
              ],
              [
                3,
                "JM Bairstow",
                89,
                180.9,
                80.5,
                81.2
              ],
              [
                4,
                "AM Rahane",
                138,
                154.3,
                106.5,
                78.9
              ],
              [
                5,
                "RK Singh",
                84,
                177.4,
                149.0,
                78.2
              ],
              [
                6,
                "PD Salt",
                207,
                179.7,
                41.3,
                78.1
              ],
              [
                7,
                "Shubman Gill",
                279,
                159.5,
                55.6,
                77.6
              ],
              [
                8,
                "Tilak Varma",
                190,
                163.7,
                44.4,
                75.7
              ],
              [
                9,
                "F du Plessis",
                162,
                164.2,
                44.3,
                75.2
              ],
              [
                10,
                "SA Yadav",
                230,
                186.1,
                38.9,
                74.9
              ],
              [
                11,
                "V Kohli",
                267,
                158.8,
                47.1,
                74.1
              ],
              [
                12,
                "S Dube",
                173,
                167.1,
                41.3,
                72.8
              ],
              [
                13,
                "DP Conway",
                149,
                143.6,
                71.3,
                72.3
              ],
              [
                13,
                "MR Marsh",
                144,
                167.4,
                40.2,
                72.3
              ],
              [
                15,
                "TM Head",
                156,
                181.4,
                35.4,
                70.9
              ],
              [
                16,
                "DA Warner",
                114,
                153.5,
                43.8,
                69.1
              ],
              [
                16,
                "Dhruv Jurel",
                112,
                183.9,
                34.3,
                69.1
              ],
              [
                18,
                "R Parag",
                156,
                177.6,
                34.6,
                68.3
              ],
              [
                19,
                "N Pooran",
                185,
                163.8,
                37.9,
                67.7
              ],
              [
                20,
                "J Fraser-McGurk",
                69,
                195.7,
                135.0,
                66.6
              ]
            ],
            "qualifiedCount": 76
          },
          {
            "id": "right_arm_off_spin",
            "title": "vs Right-arm off-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "B Sai Sudharsan",
                64,
                160.9,
                103.0,
                56.3
              ],
              [
                2,
                "TM Head",
                56,
                171.4,
                96.0,
                50.4
              ],
              [
                3,
                "Shubman Gill",
                72,
                175.0,
                42.0,
                44.6
              ],
              [
                4,
                "N Wadhera",
                52,
                134.6,
                70.0,
                31.2
              ],
              [
                5,
                "KL Rahul",
                69,
                133.3,
                46.0,
                29.0
              ],
              [
                6,
                "F du Plessis",
                55,
                105.5,
                58.0,
                26.4
              ],
              [
                7,
                "N Rana",
                62,
                150.0,
                31.0,
                22.3
              ],
              [
                8,
                "YBK Jaiswal",
                52,
                136.5,
                35.5,
                20.8
              ],
              [
                9,
                "JC Buttler",
                53,
                164.2,
                29.0,
                20.1
              ],
              [
                9,
                "V Kohli",
                53,
                101.9,
                54.0,
                20.1
              ],
              [
                11,
                "VR Iyer",
                50,
                128.0,
                21.3,
                4.0
              ]
            ],
            "qualifiedCount": 11
          },
          {
            "id": "right_arm_leg_spin",
            "title": "vs Right-arm leg-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "F du Plessis",
                55,
                109.1,
                60.0,
                33.0
              ],
              [
                2,
                "Shubman Gill",
                51,
                156.9,
                40.0,
                20.4
              ]
            ],
            "qualifiedCount": 2
          },
          {
            "id": "leg_spin",
            "title": "vs Leg-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "SA Yadav",
                184,
                169.6,
                312.0,
                91.2
              ],
              [
                2,
                "SV Samson",
                93,
                181.7,
                84.5,
                79.9
              ],
              [
                3,
                "Shubman Gill",
                124,
                148.4,
                92.0,
                73.2
              ],
              [
                4,
                "H Klaasen",
                92,
                180.4,
                55.3,
                69.1
              ],
              [
                5,
                "N Wadhera",
                118,
                155.9,
                61.3,
                68.8
              ],
              [
                6,
                "AR Patel",
                105,
                166.7,
                43.8,
                64.4
              ],
              [
                7,
                "B Sai Sudharsan",
                87,
                150.6,
                65.5,
                59.0
              ],
              [
                8,
                "A Raghuvanshi",
                67,
                167.2,
                112.0,
                58.5
              ],
              [
                9,
                "KL Rahul",
                115,
                111.3,
                128.0,
                56.6
              ],
              [
                10,
                "RM Patidar",
                72,
                225.0,
                54.0,
                53.1
              ],
              [
                11,
                "N Pooran",
                64,
                204.7,
                65.5,
                51.5
              ],
              [
                12,
                "YBK Jaiswal",
                82,
                120.7,
                null,
                51.2
              ],
              [
                13,
                "JC Buttler",
                74,
                156.8,
                58.0,
                50.2
              ],
              [
                14,
                "S Dube",
                92,
                166.3,
                30.6,
                48.0
              ],
              [
                15,
                "V Kohli",
                155,
                126.5,
                49.0,
                46.8
              ],
              [
                16,
                "SS Iyer",
                67,
                162.7,
                54.5,
                45.8
              ],
              [
                17,
                "Nithish Kumar Reddy",
                57,
                157.9,
                90.0,
                45.6
              ],
              [
                18,
                "C Green",
                56,
                141.1,
                null,
                42.6
              ],
              [
                19,
                "Tilak Varma",
                127,
                135.4,
                34.4,
                42.4
              ],
              [
                20,
                "T Stubbs",
                61,
                145.9,
                89.0,
                42.0
              ]
            ],
            "qualifiedCount": 42
          },
          {
            "id": "off_spin",
            "title": "vs Off-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "H Klaasen",
                82,
                182.9,
                150.0,
                61.5
              ],
              [
                2,
                "N Pooran",
                69,
                184.1,
                127.0,
                50.6
              ],
              [
                3,
                "YBK Jaiswal",
                54,
                190.7,
                null,
                48.6
              ],
              [
                4,
                "V Kohli",
                82,
                139.0,
                114.0,
                47.8
              ],
              [
                5,
                "S Dube",
                89,
                118.0,
                105.0,
                40.1
              ],
              [
                6,
                "Shubman Gill",
                75,
                172.0,
                64.5,
                37.5
              ],
              [
                7,
                "SA Yadav",
                55,
                120.0,
                null,
                34.8
              ],
              [
                8,
                "KL Rahul",
                57,
                110.5,
                null,
                30.4
              ],
              [
                9,
                "B Sai Sudharsan",
                50,
                152.0,
                76.0,
                25.9
              ],
              [
                10,
                "AR Patel",
                72,
                120.8,
                29.0,
                19.2
              ],
              [
                11,
                "AK Markram",
                59,
                115.2,
                34.0,
                12.8
              ],
              [
                12,
                "Ishan Kishan",
                51,
                133.3,
                22.7,
                12.8
              ],
              [
                13,
                "A Badoni",
                53,
                105.7,
                14.0,
                0.0
              ]
            ],
            "qualifiedCount": 13
          },
          {
            "id": "la_orthodox",
            "title": "vs LA Orthodox",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "B Sai Sudharsan",
                121,
                167.8,
                101.5,
                85.0
              ],
              [
                2,
                "Shubman Gill",
                131,
                133.6,
                87.5,
                70.0
              ],
              [
                3,
                "F du Plessis",
                140,
                136.4,
                63.7,
                67.9
              ],
              [
                4,
                "Tilak Varma",
                76,
                146.1,
                111.0,
                63.5
              ],
              [
                5,
                "RD Gaikwad",
                62,
                171.0,
                106.0,
                54.9
              ],
              [
                6,
                "V Kohli",
                185,
                126.0,
                58.2,
                54.3
              ],
              [
                7,
                "KL Rahul",
                60,
                155.0,
                null,
                54.0
              ],
              [
                8,
                "SS Iyer",
                67,
                134.3,
                null,
                52.7
              ],
              [
                9,
                "Ishan Kishan",
                75,
                148.0,
                55.5,
                50.9
              ],
              [
                10,
                "RG Sharma",
                91,
                135.2,
                41.0,
                49.4
              ],
              [
                11,
                "YBK Jaiswal",
                62,
                135.5,
                84.0,
                43.4
              ],
              [
                12,
                "SA Yadav",
                91,
                140.7,
                25.6,
                42.2
              ],
              [
                13,
                "RM Patidar",
                53,
                158.5,
                84.0,
                41.7
              ],
              [
                14,
                "Nithish Kumar Reddy",
                62,
                153.2,
                47.5,
                41.2
              ],
              [
                15,
                "Dhruv Jurel",
                61,
                123.0,
                null,
                40.9
              ],
              [
                16,
                "MR Marsh",
                89,
                129.2,
                38.3,
                39.4
              ],
              [
                17,
                "R Parag",
                90,
                122.2,
                36.7,
                32.8
              ],
              [
                18,
                "JC Buttler",
                62,
                132.3,
                41.0,
                31.4
              ],
              [
                19,
                "PD Salt",
                56,
                180.4,
                25.2,
                29.6
              ],
              [
                20,
                "H Klaasen",
                87,
                132.2,
                23.0,
                27.3
              ]
            ],
            "qualifiedCount": 29
          },
          {
            "id": "wrist_spin",
            "title": "vs Wrist-spin",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "SR",
              "Avg",
              "Composite"
            ],
            "rows": [
              [
                1,
                "R Parag",
                57,
                145.6,
                83.0,
                57.0
              ],
              [
                2,
                "V Kohli",
                76,
                143.4,
                54.5,
                38.0
              ],
              [
                3,
                "SA Yadav",
                54,
                129.6,
                23.3,
                0.0
              ]
            ],
            "qualifiedCount": 3
          }
        ]
      },
      {
        "id": "bowler_vs_handedness",
        "title": "Bowler vs Batter Handedness",
        "description": "Bowler effectiveness against left-hand and right-hand batters. Composite: Economy percentile (50%) + SR percentile (50%). Min 50 balls. Sample-size weighted (target: 100 balls).",
        "subcategories": [
          {
            "id": "left_hand",
            "title": "vs Left-Hand Batters",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Wkts",
              "Econ",
              "Composite"
            ],
            "rows": [
              [
                1,
                "M Prasidh Krishna",
                107,
                9,
                6.84,
                96.2
              ],
              [
                1,
                "JJ Bumrah",
                210,
                17,
                5.94,
                96.2
              ],
              [
                3,
                "Noor Ahmad",
                219,
                18,
                7.89,
                92.4
              ],
              [
                4,
                "RD Chahar",
                127,
                8,
                6.94,
                87.5
              ],
              [
                5,
                "M Pathirana",
                213,
                21,
                8.99,
                81.5
              ],
              [
                6,
                "VG Arora",
                167,
                13,
                8.95,
                78.3
              ],
              [
                6,
                "DL Chahar",
                184,
                11,
                8.25,
                78.3
              ],
              [
                6,
                "Rashid Khan",
                317,
                19,
                8.27,
                78.3
              ],
              [
                9,
                "JR Hazlewood",
                104,
                11,
                9.29,
                77.2
              ],
              [
                10,
                "TA Boult",
                285,
                17,
                8.46,
                76.1
              ],
              [
                11,
                "SP Narine",
                232,
                12,
                7.55,
                75.0
              ],
              [
                12,
                "MM Ali",
                119,
                6,
                6.45,
                74.5
              ],
              [
                13,
                "PP Chawla",
                161,
                9,
                8.68,
                70.1
              ],
              [
                14,
                "Sandeep Sharma",
                252,
                13,
                8.38,
                69.0
              ],
              [
                15,
                "Ravi Bishnoi",
                268,
                14,
                8.78,
                66.8
              ],
              [
                16,
                "WG Jacks",
                93,
                7,
                9.29,
                66.7
              ],
              [
                17,
                "Mukesh Kumar",
                227,
                18,
                9.81,
                65.8
              ],
              [
                18,
                "Arshdeep Singh",
                301,
                24,
                9.87,
                65.2
              ],
              [
                19,
                "Kuldeep Yadav",
                317,
                15,
                8.08,
                64.1
              ],
              [
                20,
                "GJ Maxwell",
                136,
                7,
                8.87,
                63.6
              ]
            ],
            "qualifiedCount": 93
          },
          {
            "id": "right_hand",
            "title": "vs Right-Hand Batters",
            "headers": [
              "Rank",
              "Player",
              "Balls",
              "Wkts",
              "Econ",
              "Composite"
            ],
            "rows": [
              [
                1,
                "TA Boult",
                388,
                28,
                8.46,
                87.2
              ],
              [
                2,
                "PP Chawla",
                233,
                16,
                8.65,
                84.4
              ],
              [
                3,
                "JJ Bumrah",
                305,
                18,
                7.18,
                83.5
              ],
              [
                4,
                "E Malinga",
                123,
                11,
                9.17,
                82.6
              ],
              [
                5,
                "M Prasidh Krishna",
                218,
                16,
                9.03,
                81.2
              ],
              [
                6,
                "CV Varun",
                498,
                30,
                7.86,
                80.7
              ],
              [
                7,
                "M Markande",
                159,
                10,
                8.79,
                78.0
              ],
              [
                8,
                "R Sai Kishore",
                246,
                16,
                8.95,
                77.5
              ],
              [
                9,
                "Mustafizur Rahman",
                161,
                12,
                9.35,
                77.1
              ],
              [
                9,
                "JR Hazlewood",
                192,
                12,
                8.72,
                77.1
              ],
              [
                11,
                "JD Unadkat",
                199,
                12,
                8.68,
                76.1
              ],
              [
                12,
                "YS Chahal",
                448,
                26,
                8.37,
                75.2
              ],
              [
                13,
                "RA Jadeja",
                422,
                21,
                7.28,
                74.8
              ],
              [
                14,
                "B Kumar",
                415,
                26,
                9.22,
                71.1
              ],
              [
                15,
                "HV Patel",
                439,
                31,
                9.62,
                70.2
              ],
              [
                16,
                "Mohammed Siraj",
                424,
                24,
                8.82,
                69.3
              ],
              [
                17,
                "M Pathirana",
                340,
                22,
                9.41,
                68.8
              ],
              [
                18,
                "Kuldeep Yadav",
                406,
                19,
                7.98,
                67.4
              ],
              [
                19,
                "MJ Santner",
                239,
                11,
                7.76,
                67.0
              ],
              [
                20,
                "Sandeep Sharma",
                318,
                21,
                9.64,
                66.5
              ]
            ],
            "qualifiedCount": 110
          }
        ]
      },
      {
        "id": "player_matchups",
        "title": "Player Matchup Rankings",
        "description": "Head-to-head dominance index. Positive = batter-favored, negative = bowler-favored. Factors: SR deviation (50%), Avg deviation (30%), Boundary% deviation (20%). Min 12 balls. Sample-size weighted (target: 50 balls).",
        "subcategories": [
          {
            "id": "batter_favored",
            "title": "Batter-Favored Matchups",
            "description": "Matchups where the batter dominates (high SR, high avg, low dismissal rate)",
            "headers": [
              "Rank",
              "Batter",
              "Bowler",
              "Balls",
              "Runs",
              "Outs",
              "SR",
              "Dominance"
            ],
            "rows": [
              [
                1,
                "H Klaasen",
                "CV Varun",
                35,
                77,
                1,
                220.0,
                44.7
              ],
              [
                2,
                "V Kohli",
                "Avesh Khan",
                34,
                70,
                1,
                205.9,
                38.5
              ],
              [
                3,
                "N Wadhera",
                "PWH de Silva",
                36,
                72,
                1,
                200.0,
                36.8
              ],
              [
                4,
                "Abhishek Sharma",
                "I Sharma",
                30,
                63,
                1,
                210.0,
                34.2
              ],
              [
                5,
                "TH David",
                "Mukesh Kumar",
                13,
                46,
                1,
                353.9,
                33.6
              ],
              [
                6,
                "SA Yadav",
                "SM Curran",
                23,
                54,
                1,
                234.8,
                30.3
              ],
              [
                7,
                "V Kohli",
                "SM Curran",
                39,
                68,
                1,
                174.4,
                29.0
              ],
              [
                8,
                "Ishan Kishan",
                "B Kumar",
                30,
                60,
                1,
                200.0,
                28.7
              ],
              [
                9,
                "RM Patidar",
                "M Markande",
                14,
                43,
                1,
                307.1,
                27.9
              ],
              [
                10,
                "KL Rahul",
                "K Rabada",
                21,
                49,
                1,
                233.3,
                26.3
              ],
              [
                11,
                "YBK Jaiswal",
                "M Jansen",
                28,
                55,
                1,
                196.4,
                26.0
              ],
              [
                12,
                "SA Yadav",
                "M Jansen",
                18,
                45,
                1,
                250.0,
                25.9
              ],
              [
                13,
                "YBK Jaiswal",
                "KK Ahmed",
                28,
                58,
                2,
                207.1,
                25.8
              ],
              [
                14,
                "T Stubbs",
                "Sandeep Sharma",
                21,
                48,
                1,
                228.6,
                25.1
              ],
              [
                15,
                "B Sai Sudharsan",
                "RA Jadeja",
                38,
                65,
                1,
                171.1,
                24.8
              ],
              [
                16,
                "YBK Jaiswal",
                "Arshdeep Singh",
                30,
                56,
                1,
                186.7,
                24.8
              ],
              [
                17,
                "TM Head",
                "Avesh Khan",
                18,
                44,
                1,
                244.4,
                24.8
              ],
              [
                18,
                "V Kohli",
                "Arshdeep Singh",
                45,
                77,
                2,
                171.1,
                24.6
              ],
              [
                19,
                "TM Head",
                "YS Chahal",
                22,
                48,
                1,
                218.2,
                24.3
              ],
              [
                20,
                "V Kohli",
                "B Kumar",
                29,
                54,
                1,
                186.2,
                24.0
              ]
            ],
            "qualifiedCount": 844
          },
          {
            "id": "bowler_favored",
            "title": "Bowler-Favored Matchups",
            "description": "Matchups where the bowler dominates (low SR, frequent dismissals)",
            "headers": [
              "Rank",
              "Batter",
              "Bowler",
              "Balls",
              "Runs",
              "Outs",
              "SR",
              "Dominance"
            ],
            "rows": [
              [
                1,
                "AR Patel",
                "CV Varun",
                24,
                12,
                1,
                50.0,
                -22.1
              ],
              [
                2,
                "RG Sharma",
                "CV Varun",
                14,
                5,
                1,
                35.7,
                -15.7
              ],
              [
                3,
                "V Kohli",
                "Harpreet Brar",
                29,
                24,
                1,
                82.8,
                -14.8
              ],
              [
                4,
                "Abishek Porel",
                "JJ Bumrah",
                20,
                14,
                1,
                70.0,
                -14.1
              ],
              [
                5,
                "T Stubbs",
                "M Pathirana",
                17,
                11,
                2,
                64.7,
                -14.1
              ],
              [
                6,
                "Ishan Kishan",
                "Ravi Bishnoi",
                23,
                19,
                2,
                82.6,
                -14.0
              ],
              [
                7,
                "JM Sharma",
                "M Jansen",
                13,
                5,
                1,
                38.5,
                -13.8
              ],
              [
                8,
                "RA Tripathi",
                "SP Narine",
                25,
                22,
                2,
                88.0,
                -13.7
              ],
              [
                9,
                "RD Gaikwad",
                "KK Ahmed",
                17,
                11,
                1,
                64.7,
                -13.2
              ],
              [
                10,
                "SV Samson",
                "RA Jadeja",
                24,
                20,
                1,
                83.3,
                -13.0
              ],
              [
                11,
                "V Kohli",
                "Ravi Bishnoi",
                18,
                13,
                1,
                72.2,
                -12.8
              ],
              [
                12,
                "RK Singh",
                "Noor Ahmad",
                18,
                13,
                2,
                72.2,
                -12.7
              ],
              [
                13,
                "Shubman Gill",
                "JJ Bumrah",
                15,
                9,
                1,
                60.0,
                -12.4
              ],
              [
                14,
                "S Dube",
                "JJ Bumrah",
                18,
                13,
                1,
                72.2,
                -12.4
              ],
              [
                15,
                "N Rana",
                "M Jansen",
                23,
                19,
                1,
                82.6,
                -12.3
              ],
              [
                16,
                "P Simran Singh",
                "TA Boult",
                31,
                31,
                3,
                100.0,
                -12.3
              ],
              [
                17,
                "KL Rahul",
                "Sandeep Sharma",
                27,
                24,
                1,
                88.9,
                -12.1
              ],
              [
                18,
                "R Parag",
                "Rashid Khan",
                23,
                21,
                2,
                91.3,
                -11.9
              ],
              [
                19,
                "JC Buttler",
                "RA Jadeja",
                15,
                10,
                1,
                66.7,
                -11.8
              ],
              [
                20,
                "Abhishek Sharma",
                "VG Arora",
                12,
                6,
                1,
                50.0,
                -11.7
              ]
            ],
            "qualifiedCount": 844
          }
        ]
      },
      {
        "id": "batter_composite",
        "title": "Overall Batter Rankings",
        "description": "Composite score: Career SR+Avg (30%) + Phase Performance (30%) + Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). Sample-size weighted. Min 500 balls.",
        "subcategories": [
          {
            "id": "overall",
            "title": "Overall Batter Rankings",
            "description": "Composite score: Career SR+Avg (30%) + Phase Performance (30%) + Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). Sample-size weighted. Min 500 balls.",
            "headers": [
              "Rank",
              "Player",
              "Inn",
              "Runs",
              "Balls",
              "SR",
              "Avg",
              "Boundary%",
              "Raw Score",
              "Weighted"
            ],
            "rows": [
              [
                1,
                "N Pooran",
                43,
                1381,
                751,
                183.9,
                46.0,
                27.7,
                86.4,
                86.4
              ],
              [
                2,
                "H Klaasen",
                39,
                1414,
                807,
                175.2,
                45.6,
                22.4,
                83.6,
                83.6
              ],
              [
                3,
                "SS Iyer",
                31,
                955,
                582,
                164.1,
                45.5,
                22.3,
                82.1,
                82.1
              ],
              [
                4,
                "SA Yadav",
                43,
                1667,
                964,
                172.9,
                47.6,
                26.4,
                81.7,
                81.7
              ],
              [
                5,
                "Shubman Gill",
                44,
                1966,
                1263,
                155.7,
                51.7,
                20.3,
                74.6,
                74.6
              ],
              [
                6,
                "TM Head",
                27,
                941,
                520,
                181.0,
                36.2,
                31.0,
                72.8,
                72.8
              ],
              [
                7,
                "B Sai Sudharsan",
                35,
                1648,
                1108,
                148.7,
                53.2,
                19.8,
                69.1,
                69.1
              ],
              [
                8,
                "YBK Jaiswal",
                43,
                1619,
                1009,
                160.5,
                41.5,
                26.5,
                68.2,
                68.2
              ],
              [
                9,
                "PD Salt",
                34,
                1056,
                595,
                177.5,
                34.1,
                29.9,
                66.1,
                66.1
              ],
              [
                10,
                "Abhishek Sharma",
                40,
                1149,
                616,
                186.5,
                30.2,
                30.2,
                64.3,
                64.3
              ],
              [
                11,
                "F du Plessis",
                38,
                1370,
                904,
                151.6,
                38.1,
                21.0,
                64.3,
                64.3
              ],
              [
                12,
                "V Kohli",
                44,
                2037,
                1390,
                146.6,
                56.6,
                19.1,
                62.9,
                62.9
              ],
              [
                13,
                "SV Samson",
                38,
                1178,
                780,
                151.0,
                38.0,
                20.6,
                59.8,
                59.8
              ],
              [
                14,
                "MR Marsh",
                26,
                816,
                516,
                158.1,
                32.6,
                23.8,
                58.8,
                58.8
              ],
              [
                15,
                "JC Buttler",
                38,
                1289,
                865,
                149.0,
                40.3,
                20.8,
                57.9,
                57.9
              ],
              [
                16,
                "Tilak Varma",
                37,
                1102,
                730,
                151.0,
                39.4,
                19.4,
                55.6,
                55.6
              ],
              [
                17,
                "RD Gaikwad",
                34,
                1295,
                891,
                145.3,
                44.7,
                19.1,
                53.7,
                53.7
              ],
              [
                18,
                "RK Singh",
                36,
                848,
                557,
                152.2,
                35.3,
                19.9,
                52.8,
                52.8
              ],
              [
                19,
                "R Parag",
                35,
                1044,
                683,
                152.9,
                36.0,
                19.9,
                51.0,
                51.0
              ],
              [
                20,
                "P Simran Singh",
                46,
                1291,
                818,
                157.8,
                29.3,
                24.9,
                50.5,
                50.5
              ]
            ],
            "qualifiedCount": 36
          }
        ]
      },
      {
        "id": "bowler_composite",
        "title": "Overall Bowler Rankings",
        "description": "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) + Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). Sample-size weighted. Min 300 balls.",
        "subcategories": [
          {
            "id": "overall",
            "title": "Overall Bowler Rankings",
            "description": "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) + Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). Sample-size weighted. Min 300 balls.",
            "headers": [
              "Rank",
              "Player",
              "Matches",
              "Balls",
              "Wkts",
              "Econ",
              "Avg",
              "Bowl SR",
              "Raw Score",
              "Weighted"
            ],
            "rows": [
              [
                1,
                "JJ Bumrah",
                25,
                595,
                38,
                6.69,
                17.4,
                15.7,
                97.6,
                97.6
              ],
              [
                2,
                "CV Varun",
                41,
                917,
                58,
                8.15,
                21.5,
                15.8,
                85.4,
                85.4
              ],
              [
                3,
                "Noor Ahmad",
                37,
                792,
                48,
                8.24,
                22.7,
                16.5,
                82.3,
                82.3
              ],
              [
                4,
                "JR Hazlewood",
                15,
                318,
                25,
                8.77,
                18.6,
                12.7,
                82.2,
                82.2
              ],
              [
                5,
                "M Prasidh Krishna",
                15,
                354,
                25,
                8.58,
                20.2,
                14.2,
                79.0,
                79.0
              ],
              [
                6,
                "M Pathirana",
                30,
                661,
                45,
                9.0,
                22.0,
                14.7,
                73.9,
                73.9
              ],
              [
                7,
                "SP Narine",
                40,
                888,
                40,
                7.58,
                28.1,
                22.2,
                73.6,
                73.6
              ],
              [
                8,
                "Kuldeep Yadav",
                39,
                870,
                41,
                7.82,
                27.7,
                21.2,
                73.2,
                73.2
              ],
              [
                9,
                "MJ Santner",
                19,
                363,
                15,
                7.64,
                30.8,
                24.2,
                71.4,
                71.4
              ],
              [
                10,
                "TA Boult",
                41,
                894,
                51,
                8.62,
                25.2,
                17.5,
                69.5,
                69.5
              ],
              [
                11,
                "PP Chawla",
                27,
                576,
                35,
                8.45,
                23.2,
                16.5,
                68.3,
                68.3
              ],
              [
                12,
                "MM Ali",
                20,
                300,
                17,
                8.1,
                23.8,
                17.6,
                67.5,
                67.5
              ],
              [
                13,
                "RA Jadeja",
                44,
                851,
                38,
                7.95,
                29.7,
                22.4,
                66.0,
                66.0
              ],
              [
                14,
                "DL Chahar",
                32,
                591,
                29,
                8.95,
                30.4,
                20.4,
                64.7,
                64.7
              ],
              [
                15,
                "Mohammed Siraj",
                43,
                966,
                50,
                8.96,
                28.8,
                19.3,
                64.4,
                64.4
              ],
              [
                16,
                "Naveen-ul-Haq",
                17,
                388,
                25,
                9.31,
                24.1,
                15.5,
                63.6,
                63.6
              ],
              [
                17,
                "Harpreet Brar",
                31,
                523,
                26,
                8.24,
                27.6,
                20.1,
                62.9,
                62.9
              ],
              [
                18,
                "KH Pandya",
                39,
                726,
                32,
                7.92,
                29.9,
                22.7,
                62.3,
                62.3
              ],
              [
                19,
                "Harshit Rana",
                30,
                619,
                39,
                9.64,
                25.5,
                15.9,
                59.5,
                59.5
              ],
              [
                20,
                "Mustafizur Rahman",
                14,
                315,
                19,
                9.33,
                25.8,
                16.6,
                59.3,
                59.3
              ]
            ],
            "qualifiedCount": 62
          }
        ]
      }
    ],
    "stats": {
      "batter_phase": 153,
      "bowler_phase": 228,
      "batter_vs_bowling_type": 295,
      "bowler_vs_handedness": 203,
      "player_matchups": 844,
      "batter_composite": 36,
      "bowler_composite": 62
    }
  },
  "metadata": {
    "generated": "2026-02-15T09:38:45Z",
    "scopes": {
      "alltime": "IPL 2008-2025 (All-Time)",
      "since2023": "IPL 2023-2025 (Since 2023)"
    },
    "defaultScope": "since2023",
    "categoriesPerScope": 7,
    "ticket": "TKT-236",
    "epic": "EPIC-021"
  }
};
