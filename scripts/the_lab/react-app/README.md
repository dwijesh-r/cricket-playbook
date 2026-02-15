# Cricket Playbook - React Dashboard

Interactive React-based dashboard for the Cricket Playbook IPL 2026 pre-tournament preview.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server (http://localhost:5173) |
| `npm run build` | TypeScript check + production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |
| `npm run format` | Format with Prettier |
| `npm run format:check` | Check formatting |
| `npm run test` | Run Vitest tests |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage |

## Folder Structure

```
react-app/
├── src/
│   ├── components/     # Reusable UI components (Layout, Nav, Cards)
│   ├── pages/          # Page-level components (Home, Comparison, WinProb)
│   ├── hooks/          # Custom React hooks (useTheme)
│   ├── data/           # Data loading utilities
│   ├── utils/          # Helper functions (formatting, rating classes)
│   ├── types/          # TypeScript type definitions
│   ├── App.tsx         # Main app with React Router
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles (Lab design system)
├── public/             # Static assets
├── tests/              # Test files
├── vite.config.ts      # Vite + Vitest configuration
├── tsconfig.json       # TypeScript configuration
├── .eslintrc.cjs       # ESLint rules
└── .prettierrc         # Prettier formatting
```

## Design System

Matches the existing Lab dashboard (`../dashboard/`):
- Dark theme by default with light theme support
- Inter font family
- CSS variables for all colors and spacing
- Glass morphism effects on navigation
- Gradient accents (blue to purple)

## Deployment

Configured for GitHub Pages at `/cricket-playbook/lab/`. The `base` path in `vite.config.ts` ensures all asset paths are correct for the deployment target.

## Data Sources

The React app will consume data from the existing Lab data files:
- `comparison_data.js` - Player comparison metrics
- `player_profiles.js` - Full player profiles
- `depth_charts.js` - Team depth charts
- `predicted_xii.js` - Predicted playing XIs

## Tech Stack

- React 18 + TypeScript
- Vite 6 (build tool)
- React Router 6 (client-side routing)
- Vitest + Testing Library (testing)
- ESLint + Prettier (code quality)
