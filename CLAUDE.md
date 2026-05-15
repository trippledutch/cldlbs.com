# CloudLabs (cldlbs.com)

Static marketing site for **CloudLabs** — independent Hyper-V Cluster Health Checks & remediation for Windows Server environments. Owner: Hans Vredevoort (hans.vredevoort@cldlbs.com).

## Stack

Pure static site. **No build step, no package.json, no dependencies.** Plain HTML/CSS/JS served as-is.

- HTML files at repo root (one per page)
- Shared `style.css` and `script.js`
- `images/` for assets
- `sitemap.xml`, `robots.txt`, `favicon.png`, `404.html`

## Pages

`index.html` (Home), `about.html`, `services.html`, `method.html`, `engagement.html`, `calculator.html`, `cases.html`, `findings.html`, `faq.html`, `book.html`, `privacy.html`, `404.html`.

## Bilingual NL/EN

The site is bilingual. Language is toggled client-side via `data-lang` on `<html>` and persisted in `localStorage` key `cl_lang`. Content for each language lives side-by-side in the same HTML — links/spans use `lang="en"` and `lang="nl"` attributes; CSS hides the inactive language.

When editing copy, **always update both EN and NL** versions of the same element.

## Versioning convention

Every file carries a version stamp. When bumping the version, update **all** of these consistently:

1. HTML comment at top of each page: `<!-- CloudLabs · vX.Y.Z · {PageName} -->`
2. Footer span in each page: `<span class="brand-version">vX.Y.Z</span>`
3. Header comment in `script.js`: `/* CloudLabs · shared script · vX.Y.Z */`
4. Header comment in `style.css`: `/* CloudLabs · shared stylesheet · vX.Y.Z */`

Commit message style: `Update cldlbs.com naar vX.Y.Z` or `Update vX.Y.Z` (Dutch, lowercase "update" also seen).

## Local development

No tooling required. Serve the directory over HTTP (file:// breaks some relative paths/CORS):

```
python3 -m http.server 8000
open http://localhost:8000
```

Stop the server: `lsof -ti:8000 | xargs kill`.

## Deployment

`origin` has **two push URLs** configured — a single `git push origin main` deploys to both:

1. **GitHub**: `https://github.com/trippledutch/cldlbs.com.git` (source of truth)
2. **Webserver**: `ssh://webadmin@trustnodes.nl:9767/var/www/cldlbs.com` (live site)

The webserver push goes directly into a bare/working repo on the host — pushing equals deploying. There is no separate CI/CD step.

Inspect targets: `git remote -v`.

## SEO / meta

Each page has canonical URL, `hreflang` alternates (en, nl, x-default all → root), Open Graph + Twitter card metadata. Preserve these when editing `<head>`.

## Style tokens

CSS custom properties defined in `:root` of `style.css` — dark theme, palette around `--bg:#0a1024`, accent `--cyan:#5fe3ff`. Body font Inter, mono JetBrains Mono.

## Consent banner

A consent banner is rendered via `.consent-banner` in CSS and toggled in `script.js`. Privacy policy lives in `privacy.html`.
