# Task: Fix Logo & TOC Consistency

## 1. LOGO
The logo (assets/logo-icon.png) must be in a fixed nav bar, FAR LEFT of viewport, 48px tall.
Teal filter: `filter:brightness(0) saturate(100%) invert(73%) sepia(30%) saturate(500%) hue-rotate(140deg) brightness(95%);`
Must be IDENTICAL position on every page — landing page and article pages with TOC sidebars.

## 2. TOC SIDEBAR (article pages only, NOT index.html)
Standardize ALL to use:
- Class: `.toc`
- Position: fixed, left:0, top: var(--nav-h), width: 280px, height: calc(100vh - var(--nav-h))
- Heading: "Contents" in mono font
- Padding: 24px 1.2rem 2rem
- Consistent link styles

## Files to edit
All .html files in this directory. Do NOT touch .js, .py, .json, .md, or assets/.

## When done
Run: `openclaw system event --text "Done: Fixed logo and TOC" --mode now`
