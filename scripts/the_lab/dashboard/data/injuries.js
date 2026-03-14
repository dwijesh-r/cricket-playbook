/**
 * Statsledge - Player Availability Tracker
 * Last updated: 2026-03-14
 *
 * Status types: 'injured', 'unavailable', 'doubtful', 'partially_available'
 */

const PLAYER_AVAILABILITY = {
    'Harshit Rana':         { status: 'injured',              team: 'KKR',  note: 'Injury', returnDate: null },
    'Matheesha Pathirana':  { status: 'injured',              team: 'KKR',  note: 'Injury', returnDate: null },
    'Wanindu Hasaranga':    { status: 'injured',              team: 'LSG',  note: 'Severe left hamstring tear — ruled out of T20 World Cup, IPL participation in doubt', returnDate: null },
    'Eshan Malinga':        { status: 'injured',              team: 'SRH',  note: 'Injury', returnDate: null },
    'Josh Hazlewood':       { status: 'doubtful',             team: 'RCB',  note: 'Right hamstring + Achilles injuries — awaiting medical clearance, doubtful for opener', returnDate: null },
    'Josh Inglis':          { status: 'partially_available',  team: 'LSG',  note: 'PA — marriage, expected to miss early matches', returnDate: null },
    'Donovan Ferreira':     { status: 'doubtful',             team: 'RR',   note: 'Shoulder fracture (SA20, Jan 2026) — recovery timeline uncertain, IPL availability doubtful', returnDate: null }
};
