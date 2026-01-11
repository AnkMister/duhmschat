# Options Portfolio Monitor - PWA

A Progressive Web App for monitoring your options portfolio with real-time ITM alerts.

## Features

- **ITM Detection**: Automatically detect when options go In-The-Money
- **Smart Alerts**: Customizable rules for expiration warnings, profit targets, and stop losses
- **Portfolio Analytics**: See your entire portfolio with P/L tracking
- **Brokerage Connection**: Connect securely via SnapTrade (OAuth-based)
- **Mobile First**: Install as PWA on iOS/Android for native-like experience
- **AI Insights**: Get AI-powered recommendations (requires OpenAI API key)

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI**: shadcn/ui + Tailwind CSS
- **Auth**: Clerk (SOC 2 Type II compliant)
- **Brokerage**: SnapTrade (SOC 2 Type 2 compliant)
- **State**: Zustand
- **Testing**: Vitest + Playwright

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env.local
   ```

3. Configure your environment variables (see `.env.example`)

4. Run development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000)

## Testing

```bash
# Unit tests
npm test

# Unit tests with coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# E2E tests with UI
npm run test:e2e:ui
```

## PWA Installation

### iOS
1. Open the app in Safari
2. Tap the Share button
3. Tap "Add to Home Screen"

### Android
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Tap "Install app" or "Add to Home screen"

## Security

- Clerk provides SOC 2 Type II compliant authentication with MFA support
- SnapTrade handles brokerage connections via OAuth (credentials never stored)
- All API routes are protected with authentication middleware
- HTTPS enforced in production

## License

Private - All rights reserved
