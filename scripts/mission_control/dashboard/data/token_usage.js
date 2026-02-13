// Auto-generated from ~/.claude/stats-cache.json
// Last updated: 2026-02-13T14:44:56Z
// Total tokens: 1.6B  |  Sessions: 8  |  Messages: 33242
//
// Regenerate:  python scripts/mission_control/generate_token_data.py

const TOKEN_DATA = {
    summary: {
        totalTokens: 1585893138,          // 1.6B
        inputTokens: 726658,          // 726.7K
        outputTokens: 68375,         // 68.4K
        cacheReadTokens: 1518815186,   // 1.5B
        cacheCreationTokens: 66282919, // 66.3M
        totalSessions: 8,
        projectSessions: 284,
        totalMessages: 33242,
        daysActive: 19,
        avgDailyTokens: 83468059,     // 83.5M
        firstSession: "2026-01-19T05:37:24.798Z",
        lastUpdated: "2026-02-13T14:44:56Z"
    },
    byModel: {
        "Claude Opus 4.5": { input: 719026, output: 37932, cacheRead: 1485904683, cacheCreation: 64919693 },  // 1.6B total
        "Claude Opus 4.6": { input: 7632, output: 30443, cacheRead: 32910503, cacheCreation: 1363226 },  // 34.3M total
    },
    daily: [
        { date: "2026-01-19", messages: 3955, sessions: 3, tools: 772, tokens: 29812, source: "stats-cache" },
        { date: "2026-01-20", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 6, source: "git-log" },
        { date: "2026-01-21", messages: 8253, sessions: 1, tools: 1811, tokens: 267663, source: "stats-cache" },
        { date: "2026-01-24", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 7, source: "git-log" },
        { date: "2026-01-25", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 15, source: "git-log" },
        { date: "2026-01-26", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 11, source: "git-log" },
        { date: "2026-01-31", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 5, source: "git-log" },
        { date: "2026-02-01", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 3, source: "git-log" },
        { date: "2026-02-02", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 6, source: "git-log" },
        { date: "2026-02-04", messages: 1931, sessions: 1, tools: 505, tokens: 133759, source: "stats-cache" },
        { date: "2026-02-05", messages: 17876, sessions: 2, tools: 4113, tokens: 325724, source: "stats-cache" },
        { date: "2026-02-06", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 61, source: "git-log" },
        { date: "2026-02-07", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 32, source: "git-log" },
        { date: "2026-02-08", messages: 1227, sessions: 1, tools: 240, tokens: 38075, source: "stats-cache" },
        { date: "2026-02-09", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 4, source: "git-log" },
        { date: "2026-02-10", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 28, source: "git-log" },
        { date: "2026-02-11", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 32, source: "git-log" },
        { date: "2026-02-12", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 121, source: "git-log" },
        { date: "2026-02-13", messages: 0, sessions: 1, tools: 0, tokens: 0, commits: 42, source: "git-log" },
    ],
    billingEstimate: {
        plan: "Claude Max",
        cycleStart: "2026-02-01",
        cycleEnd: "2026-03-01",
        daysRemaining: 16,
        note: "Subscription plan - no per-token charges"
    }
};

// Helper: format large token counts for display
function formatTokens(n) {
    if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return n.toString();
}

// Helper: format token count with commas
function formatTokensComma(n) {
    return n.toLocaleString();
}
