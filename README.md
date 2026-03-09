# TestMachine Research Library

Strategic analysis, market intelligence, and technical research for TestMachine's smart contract security platform and emerging opportunities in Web3.

## Overview

This research library contains comprehensive analysis across multiple domains:

- **Strategic Research** - Board correspondence analysis, product roadmaps, execution plans
- **Market Intelligence** - Competitive analysis, TAM sizing, emerging opportunities  
- **Technical Analysis** - Security frameworks, agentic AI systems, blockchain infrastructure
- **Customer Research** - Marketing strategies, acquisition plans, conversion optimization

## Live Site

The research library is hosted at [research.lightscalar.net](https://research.lightscalar.net)

## Structure

- `index.html` - Research library homepage with search and filtering
- `manifest.json` - Report metadata and categorization
- `assets/` - Images, logos, and design resources
- `*.html` - Individual research reports
- `server.py` - Local development server with authentication

## Design System

All reports follow a consistent design system:
- **Fonts:** Source Serif 4 (body), Manrope (headings), JetBrains Mono (UI)
- **Colors:** Dark theme with oklch color space
- **Layout:** Responsive grid with sidebar navigation
- **Components:** Standardized metrics cards, tables, callouts

## Development

### Local Server
```bash
python server.py
```

### Adding New Reports
1. Use `paul-hsu-response-strategy.html` as the canonical template
2. Update `manifest.json` with report metadata
3. Rebuild `index.html` with new entry
4. Ensure design consistency across all elements

## Content Categories

- **Strategy** - Business strategy, execution plans, board materials
- **Market** - Market analysis, competitive intelligence, opportunity sizing
- **Technical** - Technical deep-dives, architecture analysis, security research

## Confidential Content

Reports marked with `"confidential": true` in the manifest require authentication to access.

---

© 2026 TestMachine. Research & analysis for internal strategy development.