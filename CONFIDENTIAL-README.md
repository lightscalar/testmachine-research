# Confidential Reports — Server-Side Access Control

## How Authentication Works

The research library uses **cookie-based authentication** managed by `server.py`.

1. **Authenticate:** Visit any page with `?key=fermi2026` (e.g., `https://research.lightscalar.net/?key=fermi2026`)
2. The server sets an `research_auth` cookie (HMAC-signed, 24h expiry)
3. All subsequent requests use the cookie — no need to keep `?key=` in the URL
4. The cookie is stateless (HMAC of expiry timestamp), so the server needs no session store

## What Happens for Unauthenticated Users

- **Index page:** Only shows public (non-confidential) reports. Confidential reports are stripped from the manifest response.
- **Confidential report URLs:** Returns a styled **403 Access Denied** page with a password input. Entering the password sets the auth cookie and redirects back.
- **Public reports:** Always accessible to everyone.

## Marking Reports as Confidential

### Option 1: Toggle Button (UI)
- On **individual report pages**, authenticated users see a floating button (bottom-right) showing 🔓 Public or 🔒 Confidential. Click to toggle.
- On the **index page**, authenticated users see a lock icon on each card. Click to toggle.

### Option 2: API
```bash
curl -X POST https://research.lightscalar.net/api/toggle-confidential \
  -H 'Content-Type: application/json' \
  -H 'Cookie: research_auth=<your_token>' \
  -d '{"file": "report-name.html"}'
```

Returns: `{"ok": true, "confidential": true/false}`

### Option 3: Edit manifest.json directly
Add `"confidential": true` to a report entry. Remove or set `false` to make it public.

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/auth-check` | GET | No | Returns `{"authenticated": true/false}` |
| `/api/toggle-confidential` | POST | Yes | Body: `{"file": "x.html"}`. Toggles confidential flag. |

## Adding the Toggle to New Reports

Add before `</body>` in any report HTML:

```html
<script src="confidential-toggle.js"></script>
```

This script auto-detects auth status and shows the floating toggle for authenticated users.
