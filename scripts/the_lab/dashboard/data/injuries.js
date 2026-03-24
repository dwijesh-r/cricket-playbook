/**
 * Statsledge - Player Availability Tracker
 * Last updated: 2026-03-23
 *
 * Status types: 'injured', 'unavailable', 'doubtful', 'partially_available'
 */

const PLAYER_AVAILABILITY = {
    'Harshit Rana':         { status: 'injured',              team: 'KKR',  note: 'Injury', returnDate: null },
    'Matheesha Pathirana':  { status: 'injured',              team: 'KKR',  note: 'Injury', returnDate: null },
    'Wanindu Hasaranga':    { status: 'injured',              team: 'LSG',  note: 'Severe left hamstring tear — ruled out of T20 World Cup, IPL participation in doubt', returnDate: null },
    'Eshan Malinga':        { status: 'injured',              team: 'SRH',  note: 'Injury', returnDate: null },
    'Josh Hazlewood':       { status: 'partially_available',  team: 'RCB',  note: 'Injury — will miss initial phase of IPL', returnDate: null },
    'Pat Cummins':          { status: 'partially_available',  team: 'SRH',  note: 'Injury — will miss initial phase of IPL', returnDate: null },
    'Jack Edwards':         { status: 'injured',              team: 'SRH',  note: 'Ruled out of IPL 2026 — replaced by David Payne', returnDate: null },
    'Nathan Ellis':         { status: 'injured',              team: 'CSK',  note: 'Ruled out of IPL 2026 — replacement yet to be named', returnDate: null },
    'Sam Curran':           { status: 'injured',              team: 'RR',   note: 'Ruled out of IPL 2026 — replaced by Dasun Shanaka', returnDate: null },
    'Lockie Ferguson':      { status: 'partially_available',  team: 'PBKS', note: 'Personal reasons — will miss initial phase of IPL', returnDate: null },
    'Nuwan Thushara':       { status: 'doubtful',             team: 'RCB',  note: 'Fitness concern — availability doubtful', returnDate: null },
    'Yash Dayal':           { status: 'unavailable',           team: 'RCB',  note: 'Ruled out — personal reasons', returnDate: null },
    'Akash Deep':           { status: 'injured',              team: 'KKR',  note: 'Ruled out of IPL 2026 — replaced by Saurabh Dubey', returnDate: null },
    'Mitchell Starc':       { status: 'partially_available',  team: 'DC',   note: 'Will miss initial phase of IPL', returnDate: null },
    'Josh Inglis':          { status: 'partially_available',  team: 'LSG',  note: 'PA — marriage, expected to miss early matches', returnDate: null },
    'Ben Duckett':          { status: 'unavailable',           team: 'DC',   note: 'Opted out of IPL 2026 to prioritize international career', returnDate: null },
    'Donovan Ferreira':     { status: 'doubtful',             team: 'RR',   note: 'Shoulder fracture (SA20, Jan 2026) — recovery timeline uncertain, IPL availability doubtful', returnDate: null },
    'Adam Milne':           { status: 'injured',              team: 'RR',   note: 'Torn left hamstring (SA20, Jan 2026) — ruled out of T20 World Cup, doubtful for early IPL matches', returnDate: null }
};
