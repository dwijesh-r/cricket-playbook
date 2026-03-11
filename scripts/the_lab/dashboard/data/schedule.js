/**
 * Statsledge - IPL 2026 Schedule Data
 * First phase: Matches 1-20 (March 28 - April 12)
 * Source: BCCI announcement, March 11 2026
 *
 * Note: Only first 20 matches released due to state assembly elections.
 * Remaining fixtures will be added once BCCI announces the full schedule.
 */

const IPL_SCHEDULE = [
    { match: 1,  date: '2026-03-28', day: 'Sat', home: 'RCB', away: 'SRH', venue: 'M Chinnaswamy Stadium', city: 'Bengaluru' },
    { match: 2,  date: '2026-03-29', day: 'Sun', home: 'MI',  away: 'KKR', venue: 'Wankhede Stadium', city: 'Mumbai' },
    { match: 3,  date: '2026-03-30', day: 'Mon', home: 'RR',  away: 'CSK', venue: 'ACA Stadium', city: 'Guwahati' },
    { match: 4,  date: '2026-03-31', day: 'Tue', home: 'PBKS', away: 'GT', venue: 'IS Bindra Stadium', city: 'Mullanpur' },
    { match: 5,  date: '2026-04-01', day: 'Wed', home: 'LSG', away: 'DC',  venue: 'Ekana Cricket Stadium', city: 'Lucknow' },
    { match: 6,  date: '2026-04-02', day: 'Thu', home: 'KKR', away: 'SRH', venue: 'Eden Gardens', city: 'Kolkata' },
    { match: 7,  date: '2026-04-03', day: 'Fri', home: 'CSK', away: 'PBKS', venue: 'MA Chidambaram Stadium', city: 'Chennai' },
    { match: 8,  date: '2026-04-04', day: 'Sat', home: 'DC',  away: 'MI',  venue: 'Arun Jaitley Stadium', city: 'Delhi' },
    { match: 9,  date: '2026-04-04', day: 'Sat', home: 'GT',  away: 'RR',  venue: 'Narendra Modi Stadium', city: 'Ahmedabad' },
    { match: 10, date: '2026-04-05', day: 'Sun', home: 'SRH', away: 'LSG', venue: 'Rajiv Gandhi Intl Stadium', city: 'Hyderabad' },
    { match: 11, date: '2026-04-05', day: 'Sun', home: 'RCB', away: 'CSK', venue: 'M Chinnaswamy Stadium', city: 'Bengaluru' },
    { match: 12, date: '2026-04-06', day: 'Mon', home: 'KKR', away: 'PBKS', venue: 'Eden Gardens', city: 'Kolkata' },
    { match: 13, date: '2026-04-07', day: 'Tue', home: 'RR',  away: 'MI',  venue: 'ACA Stadium', city: 'Guwahati' },
    { match: 14, date: '2026-04-08', day: 'Wed', home: 'DC',  away: 'GT',  venue: 'Arun Jaitley Stadium', city: 'Delhi' },
    { match: 15, date: '2026-04-09', day: 'Thu', home: 'KKR', away: 'LSG', venue: 'Eden Gardens', city: 'Kolkata' },
    { match: 16, date: '2026-04-10', day: 'Fri', home: 'RR',  away: 'RCB', venue: 'ACA Stadium', city: 'Guwahati' },
    { match: 17, date: '2026-04-11', day: 'Sat', home: 'PBKS', away: 'SRH', venue: 'IS Bindra Stadium', city: 'Mullanpur' },
    { match: 18, date: '2026-04-11', day: 'Sat', home: 'CSK', away: 'DC',  venue: 'MA Chidambaram Stadium', city: 'Chennai' },
    { match: 19, date: '2026-04-12', day: 'Sun', home: 'LSG', away: 'GT',  venue: 'Ekana Cricket Stadium', city: 'Lucknow' },
    { match: 20, date: '2026-04-12', day: 'Sun', home: 'MI',  away: 'RCB', venue: 'Wankhede Stadium', city: 'Mumbai' }
];

const SCHEDULE_META = {
    totalMatches: 84,
    announcedMatches: 20,
    seasonStart: '2026-03-28',
    seasonEnd: '2026-05-31',
    phaseNote: 'Only first 20 matches announced. Remaining fixtures pending due to state assembly elections.',
    source: 'BCCI, March 11, 2026'
};

// Venue metadata for filtering
const SCHEDULE_VENUES = {
    'M Chinnaswamy Stadium': { city: 'Bengaluru', bias: 'pace' },
    'Wankhede Stadium': { city: 'Mumbai', bias: 'pace' },
    'ACA Stadium': { city: 'Guwahati', bias: 'neutral' },
    'IS Bindra Stadium': { city: 'Mullanpur', bias: 'neutral' },
    'Ekana Cricket Stadium': { city: 'Lucknow', bias: 'neutral' },
    'Eden Gardens': { city: 'Kolkata', bias: 'spin' },
    'MA Chidambaram Stadium': { city: 'Chennai', bias: 'spin' },
    'Arun Jaitley Stadium': { city: 'Delhi', bias: 'neutral' },
    'Narendra Modi Stadium': { city: 'Ahmedabad', bias: 'neutral' },
    'Rajiv Gandhi Intl Stadium': { city: 'Hyderabad', bias: 'pace' }
};
