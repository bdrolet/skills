---
name: scraping-linkedin-profile
description: Use when scraping, fetching, or refreshing Ben's LinkedIn profile data, or saving the LinkedIn profile to a Markdown file.
compatibility: Requires Node.js, npm, and Google Chrome installed. Uses Playwright with system Chrome.
metadata:
  depends-on: using-1password-cli
---

# Scraping LinkedIn Profile

Automates login to LinkedIn using credentials and TOTP from 1Password, then scrapes Ben's profile page to a Markdown file.

## Prerequisites

Playwright is pre-installed alongside the script — no setup needed:

```
skills/scraping-linkedin-profile/scripts/
├── scrape.js
├── package.json
└── node_modules/playwright/
```

## Credentials

Fetched automatically from 1Password (Sales vault, item: **"Ben - LinkedIn"**):

```bash
LI_EMAIL=$(op item get "Ben - LinkedIn" --vault Sales --fields label=username)
LI_PASS=$(op item get "Ben - LinkedIn" --vault Sales --fields label=password --reveal)
# TOTP: op item get "Ben - LinkedIn" --vault Sales --otp
```

## Running the Scraper

```bash
SKILL_DIR="/Users/ben/.claude/skills/scraping-linkedin-profile/scripts" && \
  LI_EMAIL="$(op item get 'Ben - LinkedIn' --vault Sales --fields label=username)" \
  LI_PASS="$(op item get 'Ben - LinkedIn' --vault Sales --fields label=password --reveal)" \
  OUT_FILE="/Users/ben/src/consulting/docs/linkedin_profile.md" \
  node "$SKILL_DIR/scrape.js"
```

## How the Script Works

### Login

LinkedIn serves a React-controlled form. Two quirks to know:

1. **Playwright visibility checks fail** on LinkedIn's inputs even though they render visibly — use `page.evaluate()` with the React `_valueTracker` trick to fill inputs without actionability checks.
2. **Wait for `domcontentloaded`** not `networkidle` — LinkedIn keeps persistent background connections that prevent networkidle from ever firing.

```js
// React-compatible fill — required for LinkedIn's controlled inputs
const fillReact = (el, val) => {
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val);
  const tracker = el._valueTracker;
  if (tracker) tracker.setValue('');
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
};
```

### TOTP

After credentials, LinkedIn redirects to `/checkpoint/challenge/`. The OTP input is `#input__phone_verification_pin`. The TOTP code is fetched live from 1Password:

```js
const otp = execSync("op item get 'Ben - LinkedIn' --vault Sales --otp").toString().trim();
await page.fill('#input__phone_verification_pin', otp);
```

### Profile Extraction

LinkedIn's class names are minified and change frequently — **do not use CSS class selectors**. Instead, strip UI chrome and grab `document.body.innerText`, then format as Markdown:

```js
const text = await page.evaluate(() => {
  document.querySelectorAll('script, style, nav, header, footer, [aria-hidden="true"]').forEach(el => el.remove());
  return document.body.innerText;
});
```

After scraping, format the raw text into structured Markdown sections (About, Experience, Education) before saving.

## Output

Saved to `/Users/ben/src/consulting/docs/linkedin_profile.md`.
