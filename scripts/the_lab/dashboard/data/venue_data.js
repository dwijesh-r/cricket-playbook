/**
 * The Lab - Venue Analysis Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: 2026-02-12T15:23:34.245295+00:00
 * Source: analytics_ipl_venue_profile_since2023,
 *         analytics_ipl_match_context_since2023,
 *         outputs/team_venue_records.csv
 */

var VENUE_DATA = {
    venueProfiles: {
        "MI": {
            venueName: "Wankhede Stadium, Mumbai",
            character: "pace",
            avgFirstInningsScore: 192.3,
            chaseFriendly: true,
            chaseWinPct: 57.1,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 9.29, boundaryPct: 24.07, dotPct: 43.25, wicketsPerMatch: 1.48 },
                    chasing: { runRate: 9.24, boundaryPct: 23.41, dotPct: 44.58, wicketsPerMatch: 1.33 }
                },
                middle: {
                    battingFirst: { runRate: 8.4, boundaryPct: 15.61, dotPct: 31.13, wicketsPerMatch: 2.81 },
                    chasing: { runRate: 9.54, boundaryPct: 22.1, dotPct: 31.02, wicketsPerMatch: 2.29 }
                },
                death: {
                    battingFirst: { runRate: 11.56, boundaryPct: 27.18, dotPct: 29.16, wicketsPerMatch: 2.38 },
                    chasing: { runRate: 10.83, boundaryPct: 23.96, dotPct: 31.3, wicketsPerMatch: 2.05 }
                }
            }
        },
        "CSK": {
            venueName: "MA Chidambaram Stadium, Chepauk, Chennai",
            character: "spin",
            avgFirstInningsScore: 171.42,
            chaseFriendly: true,
            chaseWinPct: 58.3,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 8.63, boundaryPct: 22.11, dotPct: 40.16, wicketsPerMatch: 1.5 },
                    chasing: { runRate: 8.84, boundaryPct: 22.11, dotPct: 40.63, wicketsPerMatch: 1.58 }
                },
                middle: {
                    battingFirst: { runRate: 7.59, boundaryPct: 11.65, dotPct: 29.63, wicketsPerMatch: 2.75 },
                    chasing: { runRate: 7.34, boundaryPct: 10.81, dotPct: 32.5, wicketsPerMatch: 2.67 }
                },
                death: {
                    battingFirst: { runRate: 9.82, boundaryPct: 19.24, dotPct: 32.67, wicketsPerMatch: 2.96 },
                    chasing: { runRate: 10.0, boundaryPct: 19.85, dotPct: 31.54, wicketsPerMatch: 1.55 }
                }
            }
        },
        "RCB": {
            venueName: "M Chinnaswamy Stadium, Bengaluru",
            character: "pace",
            avgFirstInningsScore: 195.38,
            chaseFriendly: false,
            chaseWinPct: 47.4,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 8.75, boundaryPct: 22.22, dotPct: 43.27, wicketsPerMatch: 1.26 },
                    chasing: { runRate: 9.44, boundaryPct: 25.0, dotPct: 41.37, wicketsPerMatch: 1.89 }
                },
                middle: {
                    battingFirst: { runRate: 9.16, boundaryPct: 18.14, dotPct: 29.12, wicketsPerMatch: 2.53 },
                    chasing: { runRate: 9.42, boundaryPct: 19.08, dotPct: 27.67, wicketsPerMatch: 2.42 }
                },
                death: {
                    battingFirst: { runRate: 11.6, boundaryPct: 26.63, dotPct: 28.86, wicketsPerMatch: 2.56 },
                    chasing: { runRate: 10.81, boundaryPct: 22.25, dotPct: 28.57, wicketsPerMatch: 2.24 }
                }
            }
        },
        "KKR": {
            venueName: "Eden Gardens, Kolkata",
            character: "pace",
            avgFirstInningsScore: 201.56,
            chaseFriendly: false,
            chaseWinPct: 45.0,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 9.48, boundaryPct: 24.21, dotPct: 42.33, wicketsPerMatch: 1.52 },
                    chasing: { runRate: 10.52, boundaryPct: 29.26, dotPct: 41.21, wicketsPerMatch: 1.52 }
                },
                middle: {
                    battingFirst: { runRate: 9.16, boundaryPct: 19.22, dotPct: 30.95, wicketsPerMatch: 2.43 },
                    chasing: { runRate: 8.76, boundaryPct: 17.66, dotPct: 31.59, wicketsPerMatch: 2.8 }
                },
                death: {
                    battingFirst: { runRate: 11.9, boundaryPct: 28.67, dotPct: 27.18, wicketsPerMatch: 2.1 },
                    chasing: { runRate: 11.69, boundaryPct: 27.38, dotPct: 32.62, wicketsPerMatch: 1.95 }
                }
            }
        },
        "DC": {
            venueName: "Arun Jaitley Stadium, Delhi",
            character: "pace",
            avgFirstInningsScore: 204.86,
            chaseFriendly: false,
            chaseWinPct: 38.9,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 10.41, boundaryPct: 29.64, dotPct: 42.04, wicketsPerMatch: 1.42 },
                    chasing: { runRate: 10.15, boundaryPct: 28.8, dotPct: 39.77, wicketsPerMatch: 1.63 }
                },
                middle: {
                    battingFirst: { runRate: 8.77, boundaryPct: 16.76, dotPct: 29.53, wicketsPerMatch: 2.47 },
                    chasing: { runRate: 8.69, boundaryPct: 17.15, dotPct: 30.6, wicketsPerMatch: 2.47 }
                },
                death: {
                    battingFirst: { runRate: 12.04, boundaryPct: 27.82, dotPct: 25.18, wicketsPerMatch: 2.21 },
                    chasing: { runRate: 10.3, boundaryPct: 21.07, dotPct: 27.69, wicketsPerMatch: 2.53 }
                }
            }
        },
        "PBKS": {
            venueName: "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
            character: "balanced",
            avgFirstInningsScore: 176.58,
            chaseFriendly: true,
            chaseWinPct: 50.0,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 8.9, boundaryPct: 22.78, dotPct: 46.11, wicketsPerMatch: 1.9 },
                    chasing: { runRate: 8.1, boundaryPct: 20.55, dotPct: 43.06, wicketsPerMatch: 1.7 }
                },
                middle: {
                    battingFirst: { runRate: 7.53, boundaryPct: 13.27, dotPct: 34.58, wicketsPerMatch: 3.7 },
                    chasing: { runRate: 8.11, boundaryPct: 14.71, dotPct: 31.18, wicketsPerMatch: 2.6 }
                },
                death: {
                    battingFirst: { runRate: 10.49, boundaryPct: 20.58, dotPct: 23.87, wicketsPerMatch: 2.56 },
                    chasing: { runRate: 10.38, boundaryPct: 20.55, dotPct: 27.4, wicketsPerMatch: 2.44 }
                }
            }
        },
        "RR": {
            venueName: "Sawai Mansingh Stadium, Jaipur",
            character: "balanced",
            avgFirstInningsScore: 191.42,
            chaseFriendly: true,
            chaseWinPct: 52.9,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 8.35, boundaryPct: 21.08, dotPct: 41.67, wicketsPerMatch: 1.18 },
                    chasing: { runRate: 9.36, boundaryPct: 25.82, dotPct: 43.95, wicketsPerMatch: 1.24 }
                },
                middle: {
                    battingFirst: { runRate: 8.92, boundaryPct: 16.01, dotPct: 25.16, wicketsPerMatch: 1.94 },
                    chasing: { runRate: 9.0, boundaryPct: 17.06, dotPct: 27.57, wicketsPerMatch: 2.29 }
                },
                death: {
                    battingFirst: { runRate: 11.66, boundaryPct: 25.55, dotPct: 22.33, wicketsPerMatch: 2.06 },
                    chasing: { runRate: 10.44, boundaryPct: 22.1, dotPct: 24.31, wicketsPerMatch: 1.6 }
                }
            }
        },
        "SRH": {
            venueName: "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
            character: "pace",
            avgFirstInningsScore: 191.5,
            chaseFriendly: true,
            chaseWinPct: 55.6,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 9.1, boundaryPct: 24.71, dotPct: 43.13, wicketsPerMatch: 1.84 },
                    chasing: { runRate: 10.16, boundaryPct: 27.62, dotPct: 41.2, wicketsPerMatch: 1.56 }
                },
                middle: {
                    battingFirst: { runRate: 8.84, boundaryPct: 17.06, dotPct: 29.82, wicketsPerMatch: 2.37 },
                    chasing: { runRate: 9.58, boundaryPct: 19.26, dotPct: 26.6, wicketsPerMatch: 2.06 }
                },
                death: {
                    battingFirst: { runRate: 11.03, boundaryPct: 24.34, dotPct: 23.64, wicketsPerMatch: 2.05 },
                    chasing: { runRate: 10.42, boundaryPct: 23.33, dotPct: 30.0, wicketsPerMatch: 1.35 }
                }
            }
        },
        "GT": {
            venueName: "Narendra Modi Stadium, Ahmedabad",
            character: "pace",
            avgFirstInningsScore: 198.84,
            chaseFriendly: false,
            chaseWinPct: 46.2,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 9.3, boundaryPct: 22.33, dotPct: 39.0, wicketsPerMatch: 1.23 },
                    chasing: { runRate: 9.0, boundaryPct: 23.29, dotPct: 44.23, wicketsPerMatch: 1.73 }
                },
                middle: {
                    battingFirst: { runRate: 9.27, boundaryPct: 17.95, dotPct: 25.93, wicketsPerMatch: 2.15 },
                    chasing: { runRate: 9.36, boundaryPct: 18.32, dotPct: 26.64, wicketsPerMatch: 2.23 }
                },
                death: {
                    battingFirst: { runRate: 11.48, boundaryPct: 24.02, dotPct: 21.78, wicketsPerMatch: 2.65 },
                    chasing: { runRate: 10.09, boundaryPct: 21.37, dotPct: 32.14, wicketsPerMatch: 2.74 }
                }
            }
        },
        "LSG": {
            venueName: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow",
            character: "balanced",
            avgFirstInningsScore: 178.2,
            chaseFriendly: true,
            chaseWinPct: 57.1,
            phases: {
                powerplay: {
                    battingFirst: { runRate: 8.13, boundaryPct: 19.07, dotPct: 42.42, wicketsPerMatch: 1.41 },
                    chasing: { runRate: 9.43, boundaryPct: 24.7, dotPct: 39.5, wicketsPerMatch: 1.1 }
                },
                middle: {
                    battingFirst: { runRate: 8.13, boundaryPct: 13.96, dotPct: 29.27, wicketsPerMatch: 2.45 },
                    chasing: { runRate: 8.28, boundaryPct: 15.96, dotPct: 32.63, wicketsPerMatch: 2.71 }
                },
                death: {
                    battingFirst: { runRate: 10.73, boundaryPct: 21.04, dotPct: 25.91, wicketsPerMatch: 2.59 },
                    chasing: { runRate: 9.02, boundaryPct: 17.49, dotPct: 34.16, wicketsPerMatch: 1.95 }
                }
            }
        }
    },
    teamVenueRecords: {
        "MI": [
            { venue: "Wankhede Stadium", city: "Mumbai", matches: 21, wins: 13, losses: 8, winPct: 61.9, record: "13-8" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 5, wins: 0, losses: 5, winPct: 0.0, record: "0-5" },
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Rajiv Gandhi International Stadium", city: "Hyderabad", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Sawai Mansingh Stadium", city: "Jaipur", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" }
        ],
        "CSK": [
            { venue: "MA Chidambaram Stadium", city: "Chennai", matches: 21, wins: 11, losses: 10, winPct: 52.4, record: "11-10" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 4, wins: 2, losses: 2, winPct: 50.0, record: "2-2" },
            { venue: "Wankhede Stadium", city: "Mumbai", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 3, wins: 1, losses: 1, winPct: 50.0, record: "1-1" },
            { venue: "M Chinnaswamy Stadium", city: "Bengaluru", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" }
        ],
        "RCB": [
            { venue: "M Chinnaswamy Stadium", city: "Bengaluru", matches: 19, wins: 9, losses: 10, winPct: 47.4, record: "9-10" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Eden Gardens", city: "Kolkata", matches: 2, wins: 1, losses: 1, winPct: 50.0, record: "1-1" },
            { venue: "Wankhede Stadium", city: "Mumbai", matches: 2, wins: 1, losses: 1, winPct: 50.0, record: "1-1" },
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 2, wins: 1, losses: 1, winPct: 50.0, record: "1-1" }
        ],
        "KKR": [
            { venue: "Eden Gardens", city: "Kolkata", matches: 21, wins: 9, losses: 11, winPct: 45.0, record: "9-11" },
            { venue: "MA Chidambaram Stadium", city: "Chennai", matches: 4, wins: 3, losses: 1, winPct: 75.0, record: "3-1" },
            { venue: "Wankhede Stadium", city: "Mumbai", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" },
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 2, wins: 2, losses: 0, winPct: 100.0, record: "2-0" }
        ],
        "DC": [
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 17, wins: 6, losses: 10, winPct: 37.5, record: "6-10" },
            { venue: "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium", city: "Visakhapatnam", matches: 4, wins: 3, losses: 1, winPct: 75.0, record: "3-1" },
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "M Chinnaswamy Stadium", city: "Bengaluru", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" }
        ],
        "PBKS": [
            { venue: "Maharaja Yadavindra Singh International Cricket Stadium", city: "Mohali", matches: 9, wins: 3, losses: 6, winPct: 33.3, record: "3-6" },
            { venue: "Himachal Pradesh Cricket Association Stadium", city: "Dharamsala", matches: 6, wins: 1, losses: 4, winPct: 20.0, record: "1-4" },
            { venue: "Punjab Cricket Association IS Bindra Stadium", city: "Chandigarh", matches: 5, wins: 1, losses: 4, winPct: 20.0, record: "1-4" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 4, wins: 3, losses: 1, winPct: 75.0, record: "3-1" },
            { venue: "MA Chidambaram Stadium", city: "Chennai", matches: 3, wins: 3, losses: 0, winPct: 100.0, record: "3-0" }
        ],
        "RR": [
            { venue: "Sawai Mansingh Stadium", city: "Jaipur", matches: 15, wins: 6, losses: 9, winPct: 40.0, record: "6-9" },
            { venue: "Barsapara Cricket Stadium", city: "Guwahati", matches: 5, wins: 2, losses: 3, winPct: 40.0, record: "2-3" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Eden Gardens", city: "Kolkata", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 3, wins: 1, losses: 1, winPct: 50.0, record: "1-1" }
        ],
        "SRH": [
            { venue: "Rajiv Gandhi International Stadium", city: "Hyderabad", matches: 19, wins: 8, losses: 10, winPct: 44.4, record: "8-10" },
            { venue: "MA Chidambaram Stadium", city: "Chennai", matches: 5, wins: 2, losses: 3, winPct: 40.0, record: "2-3" },
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 4, wins: 0, losses: 4, winPct: 0.0, record: "0-4" },
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 3, wins: 3, losses: 0, winPct: 100.0, record: "3-0" },
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" }
        ],
        "GT": [
            { venue: "Narendra Modi Stadium", city: "Ahmedabad", matches: 22, wins: 12, losses: 10, winPct: 54.5, record: "12-10" },
            { venue: "M Chinnaswamy Stadium", city: "Bengaluru", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Sawai Mansingh Stadium", city: "Jaipur", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Arun Jaitley Stadium", city: "Delhi", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" }
        ],
        "LSG": [
            { venue: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium", city: "Lucknow", matches: 21, wins: 9, losses: 11, winPct: 45.0, record: "9-11" },
            { venue: "Rajiv Gandhi International Stadium", city: "Hyderabad", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Eden Gardens", city: "Kolkata", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "Sawai Mansingh Stadium", city: "Jaipur", matches: 3, wins: 2, losses: 1, winPct: 66.7, record: "2-1" },
            { venue: "MA Chidambaram Stadium", city: "Chennai", matches: 3, wins: 1, losses: 2, winPct: 33.3, record: "1-2" }
        ]
    }
};
