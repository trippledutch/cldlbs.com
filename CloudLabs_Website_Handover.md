# CloudLabs Website — Project Handover

**Purpose of this document:** capture everything a fresh conversation needs to continue work on the CloudLabs website without re-deriving decisions or re-asking questions already answered.

**Project owner:** Hans Vredevoort (hans.vredevoort@cldlbs.com), Bangkok, TH
**Document date:** 14 May 2026
**Current deliverable:** `cloudlabs.html` (~270 KB, single self-contained file)
**Build script:** `build_site.py` (Python, assembles the HTML from a template plus base64-encoded images)

---

## 1. What the site is

A single-file, self-contained marketing website for CloudLabs, the consultancy practice of Hans Vredevoort. The site offers Hyper-V Health Checks, cluster remediation and related services for Windows Server environments.

**Key product decisions already made and locked in:**

- Single HTML file, no server needed, opens from disk or any host
- Bilingual EN/NL with a toggle in the header, preference persisted in localStorage
- Tabbed single-screen app on mobile, no page-scroll. Seven tabs: Home, Services, Method, Findings, Engagement, About, Book
- Dark technical aesthetic: navy `#0a1024` base, cyan `#5fe3ff` accent, JetBrains Mono for labels, Fraunces for display, Inter Tight for body
- No emdashes (—) or endashes (–) anywhere. Use commas, periods, or a middle dot (·)

---

## 2. Current site contents tab by tab

### Home
- Headline in three lines: "Independent and structured" / "Hyper-V Cluster Health Checks" (one line, no wrap on desktop) / "for Windows Server and Clusters"
- Three stats: 40+y in server & cluster tech, 10y MVP recognition, €165 per hour, no VAT
- Three CTAs: Book an intake, See services, How findings look
- Hero visual: cluster photo on the right with four status chips overlaid (NODE_01 ONLINE, STORAGE HEALTHY, W32TIME DRIFT 0.4s amber, CSV BALANCE 98%)

### Services
Nine cards: Hyper-V Cluster Health Check, Multisite Cluster Assessment, Storage Health Check, S2D & Azure Local Readiness, Firmware Upgrades, Windows Upgrades, Action List & Remediation, Cluster Migration, Architecture Review & Sparring.

"Stretch" was replaced with "Multisite" everywhere on user request.

### Method
Five steps: Intake & problem definition, Scripted inventory, Analysis against best practice, Findings document, Action list (optional).

### Findings
Three switchable example findings selected via pill buttons + prev/next arrows. Default is F22.

- **F22 Networking · Live Migration** (High) — Live Migration over heartbeat network
- **F12 Cluster Configuration · Quorum** (High) — File Share Witness on single non-redundant server
- **F18 Cluster Configuration · CSV Ownership** (Medium) — 7 of 8 CSVs owned by one node

Each card uses the locked finding structure: Status, Current situation, Best Practice, Deviation, Recommendation, Reference. Risk chip in the top-right (HOOG/MIDDEL/LAAG/GEEN colour-coded).

An earlier F27 (PDC emulator NTP) finding was rejected as not cluster-specific enough.

### Engagement
- €165/hour, green "no VAT" badge (invoiced from outside Europe)
- Six indicative hour blocks in two rows of three: 9 / 18 / 36 / 72 / 144 / 288
- Six terms in a single column: Delivery, On-site, Deliverable, Languages, References, NDA & privacy

### About
- Tagline: "Server & Cluster Engineering & Consultancy"
- Portrait card with photo, MVP badge, name, role, location (Bangkok), languages (Dutch/English), email, LinkedIn
- Three bio paragraphs covering: 40+ years in Microsoft world, MVP for 10+ years, co-author of Microsoft Private Cloud Computing, technical editor on Mastering Hyper-V Deployment, founder of Hyper-V.nu (retired), co-host Hyper-V Amigos
- Twelve specialisation tags

### Book
- Left: email intake form (mailto:hans.vredevoort@cldlbs.com) with name, email, organisation, service dropdown, indicative block dropdown, notes
- Right: Calendly iframe embedded at `https://calendly.com/hans-vredevoort-cldlbs/30min` with "Open in new tab" fallback

---

## 3. Header

- No logo image — request was to drop it
- Wordmark only: "Cloud" in light (`#e6ecff`), "Labs" in cyan (`#5fe3ff`), with initial caps
- Tagline below: "DECADES OF SERVER EXPERTISE"
- EN/NL toggle, top-right

---

## 4. Files in the project

**Source files used by the build script (in `/home/claude/` during build, originals in project files):**

- `build_site.py` — Python script that assembles the HTML
- `hero2_b64.txt` — base64 of the cluster photo (three glowing server cabinets)
- `portrait_b64.txt` — base64 of Hans's portrait photo for the About tab
- The previous `logo_icon_b64.txt` is no longer referenced (logo removed)

**Output:**
- `cloudlabs.html` — the single deliverable, ~270 KB

**Source images uploaded over the course of the project (in `/mnt/project/`):**
- `CloudLabs.png` — original wordmark logo (dark navy, replaced)
- `A_modern_sleek_look__Incorporation_of_cloud_and_server_elements__Predominantly_blue_color_sc.png` — early hero candidate
- `rectangular1.jpeg`, `th.jpeg`, `trippledutch.jpeg` — early hero candidates
- The current hero photo (three cluster servers, dark background) and the icon-only logo (cluster-in-cloud with arrow) were uploaded mid-project

---

## 5. Decisions and constraints to carry forward

**User communication style (from earlier conversations, still applies):**
- Concise, directive corrections expected to be incorporated without re-confirmation
- Push back when something is questionable rather than agreeing for politeness
- Never use the word "honest", never use "this explains everything", no flattery
- No emdashes, ever
- Ask before generating lengthy deliverables that cost many tokens

**Site rules:**
- No emdashes, no endashes
- Bilingual content always paired: every `<span lang="en">` has a matching `<span lang="nl">` or the toggle breaks
- All assets embedded as base64 to keep the file self-contained
- Calendly iframe needs internet to render; opens-in-new-tab button is always available as fallback
- Calendly may block embedding on `file://` origins — when hosted on a real domain, it renders inline

**Style locked in:**
- Fraunces (display, italic accents on hero headline)
- Inter Tight (body)
- JetBrains Mono (labels, eyebrows, button text)
- Navy `#0a1024` base, cyan `#5fe3ff` accent, magenta `#ff5d7a` as occasional secondary

---

## 6. Open / probable next requests

Based on the trajectory of the conversation, the most likely next moves:

1. Hosting decision — currently a static file. Could go on Netlify, GitHub Pages, Azure Static Web Apps, or any web server
2. Custom domain (cloudlabs something) and HTTPS
3. A favicon and Open Graph meta tags for link previews on LinkedIn, WhatsApp, etc.
4. Light refinements after Hans tests it on his own iPhone and tablet
5. Additional findings in the carousel as new engagements yield good examples
6. Possible swap of the cluster hero photo for something custom or branded
7. Translation review of the Dutch by a native eye

None of the above is committed work — these are likely topics.

---

## 7. How to restart in a new conversation

A fresh conversation should be able to pick up by:

1. Reading this handover doc
2. Reading `cloudlabs.html` to see current state
3. Asking the user what's next

If rebuilding from scratch is needed, the recipe is:

1. Source images live in the project files (`/mnt/project/`)
2. The build script reads two base64 text files (`hero2_b64.txt` and `portrait_b64.txt`) and a long Python string containing the HTML template
3. Running `python3 build_site.py` writes `/home/claude/cloudlabs.html`
4. That file is copied to `/mnt/user-data/outputs/cloudlabs.html` for delivery

The HTML template is around 700 lines. Any edit can be made with `str_replace` on the build script, then a single rebuild.

---

## 8. Quick reference

| Item | Value |
|---|---|
| Email | hans.vredevoort@cldlbs.com |
| LinkedIn | https://www.linkedin.com/in/hans-vredevoort-9531b5385/ |
| Calendly | https://calendly.com/hans-vredevoort-cldlbs/30min |
| Location | Bangkok, TH |
| Hourly rate | €165, no VAT (invoiced from outside Europe) |
| Hour blocks | 9 / 18 / 36 / 72 / 144 / 288 |
| Languages offered | Dutch and English |
| Delivery model | Remote-first, on-site possible at cost |
| Current file size | ~270 KB |
| Default tab on load | Home |
| Default finding shown | F22 Networking |

---

End of handover.
