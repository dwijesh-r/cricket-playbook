/**
 * Agent Caricature Avatar System
 * SVG avatars for Cricket Playbook Mission Control
 *
 * Each avatar is a 64x64 stylized cartoon face with team colors
 * and distinctive features for each agent.
 */

const AgentAvatars = {
    // Tom Brady - Patriots - Strong jaw, determined look
    'Tom Brady': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="brady-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#002244"/>
                <stop offset="100%" style="stop-color:#c60c30"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#brady-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="34" rx="18" ry="20" fill="#F5D0B0"/>
        <!-- Strong jaw -->
        <path d="M14 38 Q20 52 32 54 Q44 52 50 38" fill="#E8C4A0"/>
        <!-- Hair -->
        <path d="M14 26 Q14 14 32 12 Q50 14 50 26 L50 20 Q50 10 32 8 Q14 10 14 20 Z" fill="#5C4033"/>
        <!-- Eyes -->
        <ellipse cx="24" cy="32" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="32" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="32" r="2" fill="#2E4A62"/>
        <circle cx="40" cy="32" r="2" fill="#2E4A62"/>
        <!-- Determined eyebrows -->
        <path d="M18 27 L28 29" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <path d="M46 27 L36 29" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 35 L34 42 L30 42 Z" fill="#E8C4A0"/>
        <!-- Confident smile -->
        <path d="M26 46 Q32 50 38 46" stroke="#8B4513" stroke-width="2" fill="none" stroke-linecap="round"/>
        <!-- Jersey number hint -->
        <text x="8" y="58" font-size="8" fill="white" font-weight="bold" opacity="0.6">12</text>
    </svg>`,

    // Stephen Curry - Warriors - Beard, friendly smile
    'Stephen Curry': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="curry-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1d428a"/>
                <stop offset="100%" style="stop-color:#ffc72c"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#curry-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="34" rx="17" ry="19" fill="#C68642"/>
        <!-- Hair (short curly) -->
        <path d="M15 26 Q15 12 32 10 Q49 12 49 26" fill="#1A1A1A"/>
        <circle cx="18" cy="20" r="3" fill="#1A1A1A"/>
        <circle cx="24" cy="16" r="3" fill="#1A1A1A"/>
        <circle cx="32" cy="14" r="3" fill="#1A1A1A"/>
        <circle cx="40" cy="16" r="3" fill="#1A1A1A"/>
        <circle cx="46" cy="20" r="3" fill="#1A1A1A"/>
        <!-- Eyes -->
        <ellipse cx="24" cy="32" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="32" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="32" r="2" fill="#3D2314"/>
        <circle cx="40" cy="32" r="2" fill="#3D2314"/>
        <!-- Friendly eyebrows -->
        <path d="M19 28 Q24 26 29 28" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M35 28 Q40 26 45 28" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <!-- Nose -->
        <ellipse cx="32" cy="40" rx="3" ry="2" fill="#B07836"/>
        <!-- Beard -->
        <path d="M18 42 Q18 54 32 56 Q46 54 46 42 Q46 48 32 50 Q18 48 18 42" fill="#1A1A1A"/>
        <!-- Big smile -->
        <path d="M24 46 Q32 52 40 46" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
        <!-- Jersey number -->
        <text x="8" y="58" font-size="8" fill="white" font-weight="bold" opacity="0.6">30</text>
    </svg>`,

    // Kevin de Bruyne - Man City - Ginger hair
    'Kevin de Bruyne': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="kdb-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#6cabdd"/>
                <stop offset="100%" style="stop-color:#1c2c5b"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#kdb-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="35" rx="17" ry="18" fill="#F5D0B0"/>
        <!-- Ginger hair -->
        <path d="M14 28 Q14 12 32 10 Q50 12 50 28" fill="#D35400"/>
        <path d="M14 24 Q20 18 28 22" fill="#D35400"/>
        <path d="M50 24 Q44 18 36 22" fill="#D35400"/>
        <path d="M18 20 L20 28" stroke="#D35400" stroke-width="3"/>
        <path d="M46 20 L44 28" stroke="#D35400" stroke-width="3"/>
        <!-- Eyes (bright blue) -->
        <ellipse cx="24" cy="33" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="33" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="33" r="2" fill="#3498DB"/>
        <circle cx="40" cy="33" r="2" fill="#3498DB"/>
        <!-- Light eyebrows -->
        <path d="M19 29 L29 29" stroke="#E67E22" stroke-width="2" stroke-linecap="round"/>
        <path d="M45 29 L35 29" stroke="#E67E22" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 36 L34 42 L30 42 Z" fill="#E8C4A0"/>
        <!-- Slight smile -->
        <path d="M27 48 Q32 51 37 48" stroke="#8B4513" stroke-width="2" fill="none" stroke-linecap="round"/>
        <!-- Stubble hint -->
        <ellipse cx="32" cy="52" rx="8" ry="3" fill="#D3835022"/>
        <!-- Jersey number -->
        <text x="8" y="58" font-size="8" fill="white" font-weight="bold" opacity="0.6">17</text>
    </svg>`,

    // Jose Mourinho - Chelsea/Roma - Silver hair, intense eyes
    'Jose Mourinho': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="mou-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#034694"/>
                <stop offset="100%" style="stop-color:#d1d3d4"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#mou-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="35" rx="17" ry="18" fill="#E8C4A0"/>
        <!-- Silver/gray hair -->
        <path d="M14 28 Q14 14 32 12 Q50 14 50 28" fill="#A0A0A0"/>
        <path d="M14 22 Q16 18 22 20" stroke="#808080" stroke-width="2"/>
        <path d="M50 22 Q48 18 42 20" stroke="#808080" stroke-width="2"/>
        <!-- Intense eyes -->
        <ellipse cx="24" cy="32" rx="5" ry="4" fill="white"/>
        <ellipse cx="40" cy="32" rx="5" ry="4" fill="white"/>
        <circle cx="24" cy="32" r="2.5" fill="#2C3E50"/>
        <circle cx="40" cy="32" r="2.5" fill="#2C3E50"/>
        <circle cx="24" cy="31" r="1" fill="white"/>
        <circle cx="40" cy="31" r="1" fill="white"/>
        <!-- Furrowed intense eyebrows -->
        <path d="M17 27 L28 30" stroke="#606060" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M47 27 L36 30" stroke="#606060" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 35 L35 43 L29 43 Z" fill="#D4B896"/>
        <!-- Serious expression -->
        <path d="M26 48 L38 48" stroke="#8B4513" stroke-width="2" stroke-linecap="round"/>
        <!-- Stubble -->
        <rect x="22" y="49" width="20" height="6" rx="3" fill="#80808030"/>
        <!-- The Special One text hint -->
        <text x="6" y="58" font-size="6" fill="white" font-weight="bold" opacity="0.5">TSO</text>
    </svg>`,

    // LeBron James - Lakers - Headband, goatee
    'LeBron James': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="lebron-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#552583"/>
                <stop offset="100%" style="stop-color:#fdb927"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#lebron-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="36" rx="17" ry="18" fill="#8B5A2B"/>
        <!-- Hair -->
        <path d="M15 28 Q15 16 32 14 Q49 16 49 28" fill="#1A1A1A"/>
        <!-- Headband -->
        <rect x="12" y="20" width="40" height="6" rx="2" fill="#552583"/>
        <rect x="12" y="22" width="40" height="2" fill="#fdb927"/>
        <!-- Eyes -->
        <ellipse cx="24" cy="34" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="34" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="34" r="2" fill="#3D2314"/>
        <circle cx="40" cy="34" r="2" fill="#3D2314"/>
        <!-- Strong eyebrows -->
        <path d="M18 30 L28 30" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
        <path d="M46 30 L36 30" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <ellipse cx="32" cy="41" rx="3.5" ry="2.5" fill="#7A4B1E"/>
        <!-- Goatee -->
        <path d="M26 48 Q32 56 38 48 L38 50 Q32 58 26 50 Z" fill="#1A1A1A"/>
        <!-- Mustache -->
        <path d="M26 46 Q32 48 38 46" stroke="#1A1A1A" stroke-width="2" fill="none"/>
        <!-- Confident smile -->
        <path d="M28 48 Q32 50 36 48" stroke="white" stroke-width="1" fill="none"/>
        <!-- Crown hint -->
        <text x="8" y="58" font-size="8" fill="#fdb927" font-weight="bold" opacity="0.7">23</text>
    </svg>`,

    // Brad Stevens - Celtics - Clean cut, glasses
    'Brad Stevens': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="stevens-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#007a33"/>
                <stop offset="100%" style="stop-color:#ba9653"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#stevens-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="35" rx="16" ry="18" fill="#F5D0B0"/>
        <!-- Clean cut hair -->
        <path d="M16 28 Q16 14 32 12 Q48 14 48 28" fill="#5C4033"/>
        <path d="M16 24 L18 28" stroke="#5C4033" stroke-width="2"/>
        <path d="M48 24 L46 28" stroke="#5C4033" stroke-width="2"/>
        <!-- Glasses frames -->
        <rect x="17" y="29" width="12" height="10" rx="2" fill="none" stroke="#333" stroke-width="1.5"/>
        <rect x="35" y="29" width="12" height="10" rx="2" fill="none" stroke="#333" stroke-width="1.5"/>
        <path d="M29 34 L35 34" stroke="#333" stroke-width="1.5"/>
        <path d="M17 34 L13 32" stroke="#333" stroke-width="1"/>
        <path d="M47 34 L51 32" stroke="#333" stroke-width="1"/>
        <!-- Eyes behind glasses -->
        <ellipse cx="23" cy="34" rx="3" ry="2.5" fill="white"/>
        <ellipse cx="41" cy="34" rx="3" ry="2.5" fill="white"/>
        <circle cx="23" cy="34" r="1.5" fill="#4A6741"/>
        <circle cx="41" cy="34" r="1.5" fill="#4A6741"/>
        <!-- Neat eyebrows -->
        <path d="M18 28 L28 28" stroke="#5C4033" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M46 28 L36 28" stroke="#5C4033" stroke-width="1.5" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 36 L33 42 L31 42 Z" fill="#E8C4A0"/>
        <!-- Professional smile -->
        <path d="M27 48 Q32 51 37 48" stroke="#8B4513" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        <!-- Celtics shamrock hint -->
        <text x="6" y="58" font-size="7" fill="white" font-weight="bold" opacity="0.5">BOS</text>
    </svg>`,

    // Brock Purdy - 49ers - Young, focused
    'Brock Purdy': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="purdy-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#aa0000"/>
                <stop offset="100%" style="stop-color:#b3995d"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#purdy-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="35" rx="16" ry="18" fill="#F5D0B0"/>
        <!-- Young guy hair -->
        <path d="M16 26 Q16 12 32 10 Q48 12 48 26" fill="#4A3728"/>
        <path d="M18 20 Q22 16 28 18" fill="#4A3728"/>
        <path d="M46 20 Q42 16 36 18" fill="#4A3728"/>
        <!-- Helmet stripe hint at top -->
        <path d="M28 8 Q32 6 36 8" stroke="#b3995d" stroke-width="2"/>
        <!-- Focused eyes -->
        <ellipse cx="24" cy="33" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="33" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="33" r="2" fill="#4A6741"/>
        <circle cx="40" cy="33" r="2" fill="#4A6741"/>
        <!-- Young energetic eyebrows -->
        <path d="M19 29 L28 29" stroke="#4A3728" stroke-width="2" stroke-linecap="round"/>
        <path d="M45 29 L36 29" stroke="#4A3728" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 36 L33 41 L31 41 Z" fill="#E8C4A0"/>
        <!-- Youthful grin -->
        <path d="M26 46 Q32 50 38 46" stroke="#8B4513" stroke-width="2" fill="none" stroke-linecap="round"/>
        <!-- Light stubble -->
        <ellipse cx="32" cy="50" rx="6" ry="3" fill="#4A372820"/>
        <!-- Jersey number -->
        <text x="8" y="58" font-size="8" fill="white" font-weight="bold" opacity="0.6">13</text>
    </svg>`,

    // Andy Flower - Zimbabwe - Cricket cap
    'Andy Flower': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="flower-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#005c2f"/>
                <stop offset="100%" style="stop-color:#fce300"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#flower-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="38" rx="16" ry="17" fill="#F5D0B0"/>
        <!-- Cricket cap -->
        <ellipse cx="32" cy="22" rx="20" ry="8" fill="#005c2f"/>
        <path d="M12 22 Q12 14 32 12 Q52 14 52 22" fill="#005c2f"/>
        <rect x="12" y="18" width="40" height="6" fill="#005c2f"/>
        <!-- Cap brim -->
        <ellipse cx="32" cy="24" rx="22" ry="4" fill="#004020"/>
        <!-- Zimbabwe emblem hint -->
        <circle cx="32" cy="16" r="3" fill="#fce300"/>
        <!-- Eyes -->
        <ellipse cx="24" cy="36" rx="4" ry="3" fill="white"/>
        <ellipse cx="40" cy="36" rx="4" ry="3" fill="white"/>
        <circle cx="24" cy="36" r="2" fill="#4A3728"/>
        <circle cx="40" cy="36" r="2" fill="#4A3728"/>
        <!-- Thoughtful eyebrows -->
        <path d="M19 32 L28 32" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <path d="M45 32 L36 32" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 38 L33 44 L31 44 Z" fill="#E8C4A0"/>
        <!-- Wise smile -->
        <path d="M27 50 Q32 53 37 50" stroke="#8B4513" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        <!-- Cricket text -->
        <text x="4" y="58" font-size="6" fill="white" font-weight="bold" opacity="0.5">ZIM</text>
    </svg>`,

    // N'Golo Kante - Chelsea/Al-Ittihad - Big smile, humble look
    "N'Golo Kanté": `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="kante-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#034694"/>
                <stop offset="100%" style="stop-color:#d1d3d4"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#kante-bg)"/>
        <!-- Face -->
        <ellipse cx="32" cy="35" rx="16" ry="18" fill="#8B5A2B"/>
        <!-- Short hair -->
        <path d="M16 28 Q16 14 32 12 Q48 14 48 28" fill="#1A1A1A"/>
        <circle cx="20" cy="22" r="2" fill="#1A1A1A"/>
        <circle cx="26" cy="18" r="2" fill="#1A1A1A"/>
        <circle cx="32" cy="16" r="2" fill="#1A1A1A"/>
        <circle cx="38" cy="18" r="2" fill="#1A1A1A"/>
        <circle cx="44" cy="22" r="2" fill="#1A1A1A"/>
        <!-- Big friendly eyes -->
        <ellipse cx="24" cy="33" rx="5" ry="4" fill="white"/>
        <ellipse cx="40" cy="33" rx="5" ry="4" fill="white"/>
        <circle cx="24" cy="33" r="2.5" fill="#3D2314"/>
        <circle cx="40" cy="33" r="2.5" fill="#3D2314"/>
        <circle cx="23" cy="32" r="1" fill="white"/>
        <circle cx="39" cy="32" r="1" fill="white"/>
        <!-- Happy humble eyebrows -->
        <path d="M18 29 Q23 27 28 29" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M36 29 Q41 27 46 29" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <!-- Nose -->
        <ellipse cx="32" cy="40" rx="3" ry="2" fill="#7A4B1E"/>
        <!-- Big genuine smile -->
        <path d="M22 46 Q32 56 42 46" stroke="#1A1A1A" stroke-width="2" fill="none"/>
        <path d="M24 48 Q32 54 40 48" fill="white"/>
        <!-- Humble blush -->
        <ellipse cx="18" cy="40" rx="3" ry="2" fill="#C0785050"/>
        <ellipse cx="46" cy="40" rx="3" ry="2" fill="#C0785050"/>
        <!-- Jersey hint -->
        <text x="8" y="58" font-size="8" fill="white" font-weight="bold" opacity="0.6">7</text>
    </svg>`,

    // Florentino Perez - Real Madrid - Suit, distinguished
    'Florentino Perez': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="flo-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#ffffff"/>
                <stop offset="100%" style="stop-color:#febe10"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#flo-bg)"/>
        <!-- Suit -->
        <path d="M8 64 L14 48 L32 52 L50 48 L56 64" fill="#1a1a1a"/>
        <!-- White shirt collar -->
        <path d="M24 52 L32 56 L40 52 L38 48 L32 50 L26 48 Z" fill="white"/>
        <!-- Tie -->
        <path d="M30 50 L32 58 L34 50 Z" fill="#034694"/>
        <!-- Face -->
        <ellipse cx="32" cy="34" rx="15" ry="17" fill="#F5D0B0"/>
        <!-- Receding gray hair -->
        <path d="M20 24 Q20 16 32 14 Q44 16 44 24" fill="#A0A0A0"/>
        <path d="M17 28 L20 24" stroke="#A0A0A0" stroke-width="2"/>
        <path d="M47 28 L44 24" stroke="#A0A0A0" stroke-width="2"/>
        <!-- Distinguished eyes -->
        <ellipse cx="25" cy="32" rx="4" ry="3" fill="white"/>
        <ellipse cx="39" cy="32" rx="4" ry="3" fill="white"/>
        <circle cx="25" cy="32" r="2" fill="#2C3E50"/>
        <circle cx="39" cy="32" r="2" fill="#2C3E50"/>
        <!-- Distinguished gray eyebrows -->
        <path d="M20 28 L30 28" stroke="#808080" stroke-width="2" stroke-linecap="round"/>
        <path d="M44 28 L34 28" stroke="#808080" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 34 L34 40 L30 40 Z" fill="#E8C4A0"/>
        <!-- Confident slight smile -->
        <path d="M27 44 Q32 47 37 44" stroke="#8B4513" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        <!-- Glasses hint -->
        <path d="M18 32 L21 32" stroke="#333" stroke-width="1"/>
        <path d="M46 32 L43 32" stroke="#333" stroke-width="1"/>
        <!-- Real Madrid crest hint -->
        <text x="4" y="12" font-size="8" fill="#034694" font-weight="bold" opacity="0.7">RM</text>
    </svg>`,

    // Pep Guardiola - Man City - Bald, turtleneck sweater
    'Pep Guardiola': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="pep-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#6cabdd"/>
                <stop offset="100%" style="stop-color:#1c2c5b"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#pep-bg)"/>
        <!-- Turtleneck sweater -->
        <path d="M10 64 L16 48 L32 50 L48 48 L54 64" fill="#1a1a1a"/>
        <rect x="22" y="46" width="20" height="8" rx="2" fill="#1a1a1a"/>
        <!-- Turtleneck collar -->
        <rect x="24" y="44" width="16" height="6" rx="2" fill="#333"/>
        <!-- Face -->
        <ellipse cx="32" cy="32" rx="16" ry="17" fill="#E8C4A0"/>
        <!-- Bald head - smooth -->
        <ellipse cx="32" cy="24" rx="16" ry="12" fill="#E0B890"/>
        <!-- Slight shine on bald head -->
        <ellipse cx="28" cy="18" rx="6" ry="4" fill="#F0C8A040"/>
        <!-- Focused intense eyes -->
        <ellipse cx="25" cy="32" rx="4" ry="3" fill="white"/>
        <ellipse cx="39" cy="32" rx="4" ry="3" fill="white"/>
        <circle cx="25" cy="32" r="2" fill="#2C3E50"/>
        <circle cx="39" cy="32" r="2" fill="#2C3E50"/>
        <!-- Tactical eyebrows -->
        <path d="M20 28 L30 29" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <path d="M44 28 L34 29" stroke="#5C4033" stroke-width="2" stroke-linecap="round"/>
        <!-- Nose -->
        <path d="M32 33 L34 39 L30 39 Z" fill="#D4B896"/>
        <!-- Stubble -->
        <ellipse cx="32" cy="44" rx="10" ry="4" fill="#5C403320"/>
        <!-- Thoughtful expression -->
        <path d="M27 44 L37 44" stroke="#8B4513" stroke-width="2" stroke-linecap="round"/>
        <!-- Ears -->
        <ellipse cx="14" cy="32" rx="3" ry="5" fill="#E0B890"/>
        <ellipse cx="50" cy="32" rx="3" ry="5" fill="#E0B890"/>
        <!-- Man City hint -->
        <text x="6" y="58" font-size="6" fill="white" font-weight="bold" opacity="0.5">MCFC</text>
    </svg>`,

    // Unassigned avatar
    'Unassigned': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="unassigned-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#3a3a3c"/>
                <stop offset="100%" style="stop-color:#1c1c1e"/>
            </linearGradient>
        </defs>
        <!-- Background -->
        <rect width="64" height="64" rx="12" fill="url(#unassigned-bg)"/>
        <!-- Generic person silhouette -->
        <circle cx="32" cy="24" r="12" fill="#636366"/>
        <ellipse cx="32" cy="54" rx="16" ry="14" fill="#636366"/>
        <!-- Question mark -->
        <text x="32" y="38" font-size="16" fill="white" text-anchor="middle" font-weight="bold">?</text>
    </svg>`
};

/**
 * Get SVG avatar for an agent
 * @param {string} agentName - The name of the agent
 * @returns {string} SVG string for the avatar
 */
function getAgentAvatar(agentName) {
    return AgentAvatars[agentName] || AgentAvatars['Unassigned'];
}

/**
 * Create a data URI from SVG string
 * @param {string} svg - SVG string
 * @returns {string} Data URI
 */
function svgToDataUri(svg) {
    const encoded = encodeURIComponent(svg)
        .replace(/'/g, '%27')
        .replace(/"/g, '%22');
    return `data:image/svg+xml,${encoded}`;
}

/**
 * Get avatar as an img element HTML string
 * @param {string} agentName - The name of the agent
 * @param {string} className - Optional CSS class
 * @returns {string} HTML img element string
 */
function getAgentAvatarImg(agentName, className = '') {
    const svg = getAgentAvatar(agentName);
    const dataUri = svgToDataUri(svg);
    return `<img src="${dataUri}" alt="${agentName}" class="${className}" style="width: 100%; height: 100%; object-fit: cover;" />`;
}

// Export for use in other modules (works in browser and Node.js)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AgentAvatars, getAgentAvatar, svgToDataUri, getAgentAvatarImg };
}
