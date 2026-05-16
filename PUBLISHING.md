# Blog publicatie-handleiding · CloudLabs

Praktische gids voor het gefaseerd publiceren van blogs op cldlbs.com.

## Wat staat er en hoe werkt het

De site heeft **10 blog posts** in [blog/](blog/), allemaal volledig geschreven (NL+EN, FAQ, schema.org, internal linking). Ze zijn niet allemaal tegelijk publiek — we publiceren ze één voor één voor een natuurlijk publicatie-ritme dat goed valt bij Google.

Een blog kan in **twee staten** zijn:

| Staat | Blog-pagina | Sitemap | Blog index | Google indexeert |
|-------|-------------|---------|------------|------------------|
| **Published** | Geen `noindex` meta | Wel in `sitemap.xml` | Card zichtbaar | Ja |
| **Draft** | `<meta robots noindex,nofollow>` | Niet in sitemap | Card in HTML-comment verborgen | Nee |

Drafts blijven bereikbaar via directe URL (bv. `https://cldlbs.com/blog/<slug>.html`) — handig voor preview-links naar collega's. Maar Google indexeert ze niet en bezoekers via blog.html zien ze niet.

## Huidige status

```
./publish.py --list
```

Toont per blog: PUBLISHED of draft.

Bij de start: **1 published** (cornerstone Top 10 Issues) + **9 drafts**.

## Een nieuwe blog publiceren

**Stap 1** — kies de blog die je wilt vrijgeven en run het script:

```
./publish.py azure-local-migration-readiness
```

Het script doet automatisch vijf dingen:
1. Verwijdert `<meta name="robots" content="noindex,nofollow">` uit het blog-bestand
2. Verwijdert de HTML-comment rond de card in `blog.html`
3. Voegt de BlogPosting entry toe aan de Blog JSON-LD op `blog.html`
4. Voegt de URL toe aan `sitemap.xml`
5. Synchroniseert cross-blog links (zie [Cross-blog links](#cross-blog-links) hieronder)

**Stap 2** — controleer de status:

```
./publish.py --list
```

**Stap 3** — commit en push:

```
git add -A
git commit -m "Publish Azure Local migration readiness blog"
git push origin main
```

Push gaat naar zowel GitHub als de webserver (`origin` heeft twee push-URLs).

**Stap 4** — optioneel: versnel Google-indexering. Ga naar [Google Search Console](https://search.google.com/search-console), bovenaan **Inspect any URL**, plak de blog-URL en klik **Request indexing**.

## Een blog terug naar draft zetten

Soms wil je een blog tijdelijk verbergen, bijvoorbeeld om te corrigeren:

```
./publish.py --unpublish azure-local-migration-readiness
```

Doet de inverse: `noindex` terug, card weer in comments, URL uit sitemap. Daarna `git commit` + `git push`. Google verwijdert hem binnen enkele dagen uit de zoekresultaten zodra hij hercrawlt.

## Cross-blog links

Een gepubliceerde blog mag niet linken naar een draft. Daarvoor gebruiken we **LINK-markers** in de bron-HTML. Elke verwijzing naar een andere blog wordt verpakt in een HTML-comment-paar:

**Inline verwijzing in een paragraaf:**

```html
Full detail in <!--LINK:live-migration-wrong-network--><a href="live-migration-wrong-network.html">Live Migration on the wrong network</a><!--/LINK:live-migration-wrong-network-->.
```

**Verwijzing in een "Related articles" lijst:**

```html
<!--LINK:csv-ownership-imbalance--><li><a href="csv-ownership-imbalance.html"><span lang="en">CSV ownership imbalance</span><span lang="nl">CSV ownership-onbalans</span></a></li><!--/LINK:csv-ownership-imbalance-->
```

Het slug in de marker (`live-migration-wrong-network`, `csv-ownership-imbalance`) is de bestandsnaam zonder `.html`.

**Wat het script doet:** `publish.py` roept bij elke publish/unpublish automatisch `sync_links()` aan. Die loopt door alle `blog/*.html` bestanden en kijkt per LINK-marker of de doel-blog gepubliceerd is.

- **Doel is published** → `<a href="...">tekst</a>` blijft staan; link is klikbaar.
- **Doel is draft** → de `<a>` wordt verstopt in een `<!--draft:...-->` comment. Inline tekst leest verder als gewone prose; een hele `<li>` wordt onzichtbaar voor de browser. Google ziet geen link naar een noindex-pagina.

De markers blijven altijd staan, dus de transitie is reversibel — publiceer je later de draft, dan herstelt `sync_links()` de `<a>` automatisch.

Je kunt sync ook handmatig forceren (bv. nadat je een nieuwe link hebt toegevoegd):

```
./publish.py --sync-links
```

**Discipline bij schrijven:** wikkel elke nieuwe cross-blog link in een LINK-marker, ook als het doel al gepubliceerd is. Dan blijft het systeem werken als je het doel ooit terugzet naar draft.

## Een geheel nieuwe blog toevoegen

Als je een **nieuwe** blog wilt toevoegen die nu nog niet bestaat:

**Stap 1** — schrijf het HTML-bestand: `blog/<slug>.html`. Gebruik een bestaande blog als template (bv. [blog/top-10-hyper-v-cluster-issues.html](blog/top-10-hyper-v-cluster-issues.html)). Belangrijk om mee te nemen:
- `<meta name="robots" content="noindex,nofollow">` (start als draft)
- `<link rel="canonical">` met de juiste URL
- `<link rel="alternate" hreflang>` voor en, nl, x-default
- BlogPosting JSON-LD met headline, datum, author
- BreadcrumbList JSON-LD
- FAQPage JSON-LD met de FAQ-vragen
- Volledig NL + EN content
- Related articles met links naar andere blogs

**Stap 2** — voeg de blog toe aan [publish.py](publish.py):

```python
BLOGS = {
    # ... bestaande entries ...
    '<slug>': 'De volledige Engelse headline van de blog',
}
```

**Stap 3** — voeg een blog card toe aan [blog.html](blog.html), gewikkeld in een DRAFT-comment:

```html
<!-- DRAFT, not yet published. Remove these comments to publish.
<a class="blog-card" href="blog/<slug>.html">
  <span class="tag">Category</span>
  <h2>
    <span lang="en">English Title</span>
    <span lang="nl">Nederlandse titel</span>
  </h2>
  <p>
    <span lang="en">English description...</span>
    <span lang="nl">Nederlandse beschrijving...</span>
  </p>
  <div class="meta">YYYY-MM-DD · X min read</div>
  <span class="read-more">Read article →</span>
</a>
-->
```

**Stap 4** — test status:

```
./publish.py --list
```

De nieuwe blog moet als `draft` verschijnen.

**Stap 5** — wanneer klaar om te publiceren, volg de standaard publish-flow hierboven.

## Versie-bump bij elke push

Conform [CLAUDE.md](CLAUDE.md) bumpen we de versie bij elke release. Update consistent in vier plekken:

1. HTML-comment bovenaan elke gewijzigde pagina: `<!-- CloudLabs · vX.Y.Z · {PageName} -->`
2. Footer span: `<span class="brand-version">vX.Y.Z</span>`
3. Header comment in [script.js](script.js): `/* CloudLabs · shared script · vX.Y.Z */`
4. Header comment in [style.css](style.css): `/* CloudLabs · shared stylesheet · vX.Y.Z */`

Commit message: `Update cldlbs.com naar vX.Y.Z` (Nederlands) of `Update vX.Y.Z`.

## Google Search Console workflow

Bij elke nieuw gepubliceerde blog:

1. **Wacht 1-3 dagen** na de push — Google ontdekt de blog automatisch via de geüpdatete sitemap
2. **Of versnel**: in GSC → **Inspect any URL** → plak de blog-URL → **Request indexing**
3. **Monitor** in GSC → **Indexing** → **Pages**: na enkele dagen moet de URL onder "Indexed" verschijnen
4. **Performance-data** (impressions, clicks per zoekwoord) verschijnt binnen 1-2 weken in GSC → **Performance**

Tip: dien niet 5 URLs tegelijk in via Request indexing. Google limiteert ~10 per dag en stapelt vragen op. Eén URL per dag is genoeg.

## Lokaal testen voor je pusht

```
python3 -m http.server 8000
open http://localhost:8000/blog.html
```

Bevestig dat:
- Alleen published blogs als card zichtbaar zijn
- Het aantal cards op blog.html matcht met `./publish.py --list`
- De gepubliceerde blogs openen zonder `noindex` in de pagina-bron

Server stoppen: `lsof -ti:8000 | xargs kill`.

## Troubleshooting

**"GSC toont nog het oude aantal URLs"** — Google cachet sitemaps 1-3 dagen. Forceer een fresh read: in GSC → Sitemaps → klik de drie puntjes naast de sitemap → Remove → opnieuw toevoegen via "Add a new sitemap" → `sitemap.xml`.

**"Een blog staat dubbel verborgen op blog.html"** — Dat kan gebeuren bij snelle unpublish na publish. Fix met deze one-liner:

```bash
python3 -c "
from pathlib import Path
p = Path('blog.html')
t = p.read_text()
dl = '      <!-- DRAFT, not yet published. Remove these comments to publish.\n'
while dl + dl in t: t = t.replace(dl + dl, dl)
cl = '      -->\n'
while cl + cl in t: t = t.replace(cl + cl, cl)
p.write_text(t)
"
```

**"Het script vindt mijn slug niet"** — Voeg hem toe aan `BLOGS = {...}` in [publish.py](publish.py).

**"Google indexeert de drafts toch"** — Onmogelijk als de `noindex` meta tag aanwezig is. Verifieer met `curl -s https://cldlbs.com/blog/<slug>.html | grep robots`. Als het niet matcht, run `./publish.py --unpublish <slug>` en push opnieuw.

## Aanbevolen ritme

Voor een nieuwe site (zoals cldlbs.com nu) is **één blog per 7-14 dagen** een natuurlijk ritme dat Google graag ziet. Patronen die we afraden:

- Alle blogs tegelijk publiceren — Google ziet dit als content-dump, ranking-signaal lager
- Te lang wachten (>4 weken) — site lijkt verlaten, terugkeer in zoekresultaten kost extra tijd

**Suggestie voor de huidige 9 drafts**, bijvoorbeeld:

| Week | Blog |
|------|------|
| 1 | csv-ownership-imbalance (sterke internal link met cornerstone) |
| 2 | live-migration-wrong-network |
| 3 | cluster-witness-comparison |
| 4 | azure-local-migration-readiness |
| 5 | vmware-to-hyper-v-migration-assessment |
| 6 | hyper-v-time-drift-kerberos-csv |
| 7 | windows-server-2025-hyper-v-cluster-features |
| 8 | cluster-aware-updating-runbook-audit-trail |
| 9 | san-vs-s2d-vs-azure-local-hyper-v-storage |

Past je niet? Pas aan op basis van seizoensgebondenheid van zoekvolume of klantbehoefte.
