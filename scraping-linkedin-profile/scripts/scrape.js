#!/usr/bin/env node
// Usage: LI_EMAIL=... LI_PASS=... OUT_FILE=... node scrape.js
// Credentials are fetched externally; see SKILL.md for the op commands.

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');

(async () => {
  const email = process.env.LI_EMAIL;
  const password = process.env.LI_PASS;
  const outFile = process.env.OUT_FILE;

  if (!email || !password || !outFile) {
    console.error('Missing LI_EMAIL, LI_PASS, or OUT_FILE');
    process.exit(1);
  }

  const browser = await chromium.launch({ channel: 'chrome', headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // --- Login ---
  await page.goto('https://www.linkedin.com/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000); // React needs time to render after domcontentloaded

  const startUrl = page.url();
  if (!startUrl.includes('checkpoint') && !startUrl.includes('challenge')) {
    console.log('Filling login form...');
    // LinkedIn uses React controlled inputs. Playwright's actionability checks fail on
    // these inputs even though they are visually rendered. Use _valueTracker to trigger
    // React's synthetic onChange before clicking the submit button.
    await page.evaluate(([e, p]) => {
      const fillReact = (el, val) => {
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val);
        const tracker = el._valueTracker;
        if (tracker) tracker.setValue('');
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      };
      fillReact(document.querySelector('input[type="email"]'), e);
      fillReact(document.querySelector('input[type="password"]'), p);
      const btn = [...document.querySelectorAll('button')].find(
        b => /sign in/i.test(b.innerText) && b.offsetHeight > 0
      );
      if (btn) btn.click();
    }, [email, password]);

    await page.waitForURL(/linkedin\.com\/(feed|checkpoint|challenge)/, { timeout: 30000 });
    await page.waitForTimeout(2000);
  }

  // --- TOTP challenge ---
  if (page.url().includes('checkpoint') || page.url().includes('challenge')) {
    console.log('TOTP required — fetching from 1Password...');
    await page.waitForSelector('#input__phone_verification_pin', { timeout: 10000 });
    const otp = execSync("op item get 'Ben - LinkedIn' --vault Sales --otp 2>/dev/null || op item get 'Ben - LinkedIn' --otp").toString().trim();
    await page.fill('#input__phone_verification_pin', otp);
    await page.click('button[type="submit"]');
    await page.waitForURL(/linkedin\.com\/feed/, { timeout: 30000 });
    console.log('Authenticated.');
  }

  // --- Navigate to profile ---
  console.log('Loading profile page...');
  await page.goto('https://www.linkedin.com/in/benjamindrolet/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);

  // Expand truncated sections
  for (const btn of await page.locator('button:has-text("see more"), button:has-text("Show more")').all()) {
    try { await btn.click({ timeout: 1000 }); await page.waitForTimeout(300); } catch {}
  }

  // --- Extract raw text (CSS class selectors break frequently; innerText is stable) ---
  const rawText = await page.evaluate(() => {
    document.querySelectorAll('script, style, nav, header, footer, [aria-hidden="true"]').forEach(el => el.remove());
    return document.body.innerText;
  });

  await browser.close();

  // --- Format as Markdown ---
  const md = formatAsMarkdown(rawText);
  fs.writeFileSync(outFile, md, 'utf8');
  console.log('Saved to', outFile);
})();

function formatAsMarkdown(raw) {
  // Strip LinkedIn UI noise (notifications, suggested widgets, analytics, etc.)
  const noisePatterns = [
    /^\d+ notifications?$/m,
    /^(Open to|Add section|Add custom button|Get started|Suggested for you|Private to you)$/m,
    /^(Show recruiters|Tell non-profits|Confirm current position|Analytics).*$/m,
    /^\d+ (profile views|post impressions|search appearances).*$/m,
    /^(Past \d+ days|Discover who|Start a post|See how often).*$/m,
    /^(Create a post|Show all|Show all pending|Received|Given \(\d+\))$/m,
    /^You haven't received.*$/m,
    /^Try asking one.*$/m,
    /^Ask for a recommendation$/m,
    /^(Profile language|Public profile & URL|Who your viewers|People you may know|You might like|Pages for you|From your school)$/m,
    /^(Top Voices|Companies|Groups|Newsletters|Schools|Interests)$/m,
    /^(Following|Connect|Message|Follow)$/m,
    /^\· \d(st|nd|rd|th)$/m,
    /^\d+,\d+ followers?$/m,
    /^www\.linkedin\.com.*$/m,
  ];

  const lines = raw.split('\n').map(l => l.trim()).filter(Boolean);
  const cleaned = lines.filter(line => !noisePatterns.some(p => p.test(line)));

  // Find key section indices
  const idx = (label) => cleaned.findIndex(l => l.toLowerCase() === label.toLowerCase());

  const nameIdx = 0;
  const headlineIdx = 1;
  const locationIdx = cleaned.findIndex(l => l.includes('United States') || l.includes('Bay Area') || l.includes('Chicago'));
  const aboutIdx = idx('About');
  const activityIdx = idx('Activity');
  const experienceIdx = idx('Experience');
  const educationIdx = idx('Education');

  const slice = (from, to) => from >= 0 && to > from ? cleaned.slice(from + 1, to) : [];

  const name = cleaned[nameIdx] || 'Ben Drolet';
  const headline = cleaned[headlineIdx] || '';
  const location = locationIdx >= 0 ? cleaned[locationIdx] : '';
  const aboutLines = slice(aboutIdx, activityIdx >= 0 ? activityIdx : experienceIdx);
  const experienceLines = slice(experienceIdx, educationIdx);
  const educationLines = educationIdx >= 0 ? cleaned.slice(educationIdx + 1, educationIdx + 20) : [];

  const out = [];
  out.push(`# ${name}`);
  out.push('');
  if (headline) out.push(`**${headline}**`);
  if (location) out.push(`*${location}*`);
  out.push('');
  out.push('LinkedIn: https://www.linkedin.com/in/benjamindrolet/');
  out.push('');

  if (aboutLines.length) {
    out.push('## About');
    out.push('');
    out.push(aboutLines.join(' '));
    out.push('');
  }

  if (experienceLines.length) {
    out.push('## Experience');
    out.push('');
    out.push(experienceLines.join('\n'));
    out.push('');
  }

  if (educationLines.length) {
    out.push('## Education');
    out.push('');
    out.push(educationLines.join('\n'));
    out.push('');
  }

  return out.join('\n');
}
