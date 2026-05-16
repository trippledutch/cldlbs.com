#!/usr/bin/env python3
"""
CloudLabs blog publish helper.

Usage:
    ./publish.py --list                 # show status of all blogs
    ./publish.py <slug>                 # publish a draft (unhide everywhere)
    ./publish.py --unpublish <slug>     # back to draft (hide everywhere)

The slug is the filename without .html, e.g.:
    ./publish.py azure-local-migration-readiness

What "publish" does:
  1. Remove <meta name="robots" content="noindex,nofollow"> from blog/<slug>.html
  2. Uncomment the blog card on blog.html
  3. Add the BlogPosting entry back to blog.html's JSON-LD
  4. Add the URL to sitemap.xml

"unpublish" does the inverse.

Idempotent. Safe to run multiple times.
"""
import re
import sys
from pathlib import Path

# slug -> headline (used in blog.html JSON-LD)
BLOGS = {
    'top-10-hyper-v-cluster-issues':
        'Hyper-V Cluster Health Check: 10 issues we keep finding in 2026',
    'azure-local-migration-readiness':
        "Azure Local Migration Readiness Checklist: What's Different in 2026",
    'csv-ownership-imbalance':
        'CSV Ownership Imbalance in Hyper-V Clusters: Causes and Fixes',
    'live-migration-wrong-network':
        'Live Migration on the Wrong Network: The Silent Hyper-V Pitfall',
    'cluster-witness-comparison':
        'File Share Witness vs Cloud Witness vs Disk Witness: Which Type Fits Your Cluster?',
    'vmware-to-hyper-v-migration-assessment':
        'VMware to Hyper-V Cluster Migration: A 6-Step Pre-Migration Assessment',
    'hyper-v-time-drift-kerberos-csv':
        'Time Drift in Hyper-V Clusters: The Silent Killer of Kerberos and CSV',
    'windows-server-2025-hyper-v-cluster-features':
        'Windows Server 2025 Hyper-V: What It Really Adds for Cluster Operators',
    'cluster-aware-updating-runbook-audit-trail':
        'Cluster Aware Updating: Runbook, Audit Trail, and What Nobody Documents',
    'san-vs-s2d-vs-azure-local-hyper-v-storage':
        'SAN vs S2D vs Azure Local: Choosing Hyper-V Storage in 2026',
}

ROOT = Path(__file__).parent
BLOG_DIR = ROOT / 'blog'
INDEX = ROOT / 'blog.html'
SITEMAP = ROOT / 'sitemap.xml'

NOINDEX_LINE = '<meta name="robots" content="noindex,nofollow">\n'

# ----------------------------------------------------------------------------

def is_published(slug):
    """A blog is published if its file has NO noindex meta tag."""
    f = BLOG_DIR / f'{slug}.html'
    if not f.exists():
        return None
    return 'name="robots"' not in f.read_text()

def list_status():
    print(f'{"Status":<10} {"Slug":<48} Headline')
    print('-' * 100)
    for slug, headline in BLOGS.items():
        st = is_published(slug)
        if st is None:
            label = 'MISSING'
        elif st:
            label = 'PUBLISHED'
        else:
            label = 'draft'
        print(f'{label:<10} {slug:<48} {headline[:50]}')

# ----------------------------------------------------------------------------

def publish_post_file(slug):
    f = BLOG_DIR / f'{slug}.html'
    t = f.read_text()
    if 'name="robots"' not in t:
        return False
    t = re.sub(r'<meta name="robots"[^>]*>\n', '', t, count=1)
    f.write_text(t)
    return True

def unpublish_post_file(slug):
    f = BLOG_DIR / f'{slug}.html'
    t = f.read_text()
    if 'name="robots"' in t:
        return False
    t = re.sub(
        r'(<meta name="viewport"[^>]*>\n)',
        r'\1' + NOINDEX_LINE,
        t,
        count=1,
    )
    f.write_text(t)
    return True

# ----------------------------------------------------------------------------

def publish_card_in_index(slug):
    """Remove the DRAFT comment wrapping the blog card on blog.html."""
    t = INDEX.read_text()
    href = f'blog/{slug}.html'
    # Match: <!-- DRAFT...\n      <a class="blog-card" href="<href>"...> ... </a>\n      -->
    pat = re.compile(
        r'\n\s*<!-- DRAFT, not yet published\. Remove these comments to publish\.\n'
        r'(\s*<a class="blog-card" href="' + re.escape(href) + r'">.*?</a>)\n'
        r'\s*-->\n',
        re.DOTALL,
    )
    new, n = pat.subn(r'\n\1\n', t, count=1)
    if n == 0:
        return False
    INDEX.write_text(new)
    return True

def unpublish_card_in_index(slug):
    """Wrap the blog card on blog.html in a DRAFT comment."""
    t = INDEX.read_text()
    href = f'blog/{slug}.html'
    # If the card already sits inside a DRAFT block, don't re-wrap.
    already_wrapped = re.search(
        r'<!-- DRAFT[^<]*<a class="blog-card" href="' + re.escape(href) + r'">',
        t,
        re.DOTALL,
    )
    if already_wrapped:
        return False
    pat = re.compile(
        r'\n(\s*<a class="blog-card" href="' + re.escape(href) + r'">.*?</a>)\n',
        re.DOTALL,
    )
    def wrap(m):
        block = m.group(1)
        return f'\n      <!-- DRAFT, not yet published. Remove these comments to publish.\n{block}\n      -->\n'
    new, n = pat.subn(wrap, t, count=1)
    if n == 0:
        return False
    INDEX.write_text(new)
    return True

# ----------------------------------------------------------------------------

def add_blogposting_jsonld(slug):
    """Add the BlogPosting entry back into blog.html JSON-LD, if missing."""
    headline = BLOGS[slug]
    url = f'https://cldlbs.com/blog/{slug}.html'
    entry = (
        f'    {{"@type":"BlogPosting","headline":"{headline}",'
        f'"url":"{url}","datePublished":"2026-05-15",'
        f'"author":{{"@type":"Person","name":"Hans Vredevoort"}}}}'
    )
    t = INDEX.read_text()
    if url in t and '"@type":"BlogPosting"' in t and slug in t.split('"blogPost":[', 1)[1].split(']', 1)[0]:
        return False  # already present
    # Insert before the closing ] of blogPost array, after the last existing entry
    pat = re.compile(r'("blogPost":\[)(.*?)(\s*\])', re.DOTALL)
    m = pat.search(t)
    if not m:
        return False
    head, body, tail = m.group(1), m.group(2), m.group(3)
    if url in body:
        return False
    # Append entry to the existing list
    if body.strip():
        new_body = body.rstrip().rstrip(',') + ',\n' + entry + '\n  '
    else:
        new_body = '\n' + entry + '\n  '
    new = t[:m.start()] + head + new_body + tail + t[m.end():]
    INDEX.write_text(new)
    return True

def remove_blogposting_jsonld(slug):
    url = f'https://cldlbs.com/blog/{slug}.html'
    t = INDEX.read_text()
    pat = re.compile(
        r',?\s*\{"@type":"BlogPosting","headline":"[^"]+","url":"'
        + re.escape(url)
        + r'","datePublished":"[^"]+","author":\{"@type":"Person","name":"[^"]+"\}\}',
    )
    new, n = pat.subn('', t, count=1)
    # Clean up dangling comma after [
    new = re.sub(r'\[\s*,', '[', new)
    new = re.sub(r',\s*,', ',', new)
    new = re.sub(r',(\s*\])', r'\1', new)
    # Collapse blank lines left behind inside the blogPost array
    new = re.sub(r'("blogPost":\[)(.*?)(\s*\])',
                 lambda m: m.group(1) + re.sub(r'\n\s*\n+', '\n', m.group(2)) + m.group(3),
                 new, count=1, flags=re.DOTALL)
    if n == 0:
        return False
    INDEX.write_text(new)
    return True

# ----------------------------------------------------------------------------

SITEMAP_URL_TEMPLATE = '''  <url>
    <loc>https://cldlbs.com/blog/{slug}.html</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://cldlbs.com/blog/{slug}.html"/>
    <xhtml:link rel="alternate" hreflang="nl" href="https://cldlbs.com/blog/{slug}.html"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://cldlbs.com/blog/{slug}.html"/>
    <lastmod>2026-05-15</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.8</priority>
  </url>
'''

def add_to_sitemap(slug):
    t = SITEMAP.read_text()
    needle = f'<loc>https://cldlbs.com/blog/{slug}.html</loc>'
    if needle in t:
        return False
    entry = SITEMAP_URL_TEMPLATE.format(slug=slug)
    t = t.replace('</urlset>', entry + '</urlset>')
    SITEMAP.write_text(t)
    return True

def remove_from_sitemap(slug):
    t = SITEMAP.read_text()
    pat = re.compile(
        r'  <url>\n'
        r'    <loc>https://cldlbs\.com/blog/' + re.escape(slug) + r'\.html</loc>\n'
        r'(?:    <xhtml:link[^\n]*\n)+'
        r'    <lastmod>[^<]+</lastmod>\n'
        r'    <changefreq>[^<]+</changefreq>\n'
        r'    <priority>[^<]+</priority>\n'
        r'  </url>\n',
    )
    new, n = pat.subn('', t, count=1)
    if n == 0:
        return False
    SITEMAP.write_text(new)
    return True

# ----------------------------------------------------------------------------

# Cross-blog link markers. Source HTML wraps each cross-blog reference like:
#
#   inline:  <!--LINK:slug--><a href="slug.html">link text</a><!--/LINK:slug-->
#   list:    <!--LINK:slug--><li><a href="slug.html">...</a></li><!--/LINK:slug-->
#
# When the target slug is a draft, sync_links() hides the link:
#   - inline anchor -> plain text (strips <a> tags, keeps inner text)
#   - <li> wrapper  -> HTML comment placeholder (entire <li> removed from render)
#
# The markers stay in place either way, so the transition is reversible.

LINK_BLOCK_RE = re.compile(
    r'<!--LINK:(?P<slug>[a-z0-9-]+)-->(?P<body>.*?)<!--/LINK:(?P=slug)-->',
    re.DOTALL,
)

# A <li> reference wraps a single <li>...</li> (possibly with surrounding whitespace).
LI_BODY_RE = re.compile(r'^\s*<li>.*</li>\s*$', re.DOTALL)
# A hidden <li> reference is stored as a placeholder we can recognise.
LI_HIDDEN_RE = re.compile(r'^<!--draft:(?P<inner><li>.*</li>)-->$', re.DOTALL)
# An inline reference is an <a> tag with optional inner markup.
INLINE_BODY_RE = re.compile(r'^<a [^>]*>(?P<text>.*)</a>$', re.DOTALL)
# A hidden inline reference stores the original anchor in a comment so we can restore it.
INLINE_HIDDEN_RE = re.compile(r'^<!--draft:(?P<inner><a [^>]*>.*</a>)-->(?P<text>.*)$', re.DOTALL)


def _transform_block(slug, body, published_slugs):
    """Return new body for a LINK block, based on whether slug is published."""
    is_pub = slug in published_slugs

    # Already in hidden-list form
    m = LI_HIDDEN_RE.match(body)
    if m:
        return m.group('inner') if is_pub else body

    # Already in hidden-inline form (comment + plain text)
    m = INLINE_HIDDEN_RE.match(body)
    if m:
        return m.group('inner') if is_pub else body

    # Live <li> form
    if LI_BODY_RE.match(body):
        if is_pub:
            return body
        # Hide the entire <li> by stashing it in a comment placeholder
        return f'<!--draft:{body.strip()}-->'

    # Live inline <a> form
    m = INLINE_BODY_RE.match(body)
    if m:
        if is_pub:
            return body
        anchor = body
        text = m.group('text')
        return f'<!--draft:{anchor}-->{text}'

    # Unknown shape — leave untouched
    return body


def wrap_links(verbose=True):
    """Walk every blog file and wrap any unmarked cross-blog references.

    Looks for <a href="<slug>.html"> inside blog files where <slug> is a known
    blog (in BLOGS) and the anchor is not already inside a LINK marker. Wraps:
      - <li>...<a href="slug.html">...</a>...</li>  -> wraps the entire <li>
      - <a href="slug.html">...</a>                 -> wraps the anchor inline
    Self-links (link target == current file) are skipped.
    """
    slugs = set(BLOGS.keys())
    # Build a single alternation for known slugs to avoid wrapping unrelated links.
    slug_alt = '|'.join(re.escape(s) for s in slugs)
    # Pattern for an <li> containing exactly one cross-blog anchor.
    li_re = re.compile(
        r'(?P<full><li>\s*<a href="(?P<slug>' + slug_alt + r')\.html">.*?</a>\s*</li>)',
        re.DOTALL,
    )
    # Pattern for a bare anchor.
    a_re = re.compile(
        r'(?P<full><a href="(?P<slug>' + slug_alt + r')\.html">.*?</a>)',
        re.DOTALL,
    )
    changed_files = 0
    for f in sorted(BLOG_DIR.glob('*.html')):
        self_slug = f.stem
        t = f.read_text()
        original = t
        # Pass 1: wrap <li> blocks first (so the inner anchor is consumed and
        # not double-wrapped by pass 2).
        def li_repl(m):
            slug = m.group('slug')
            if slug == self_slug:
                return m.group('full')
            # Skip if already inside a LINK marker
            start = m.start()
            preceding = t[max(0, start - 80):start]
            if f'<!--LINK:{slug}-->' in preceding and '<!--/LINK:' not in preceding.split(f'<!--LINK:{slug}-->')[-1]:
                return m.group('full')
            return f'<!--LINK:{slug}-->{m.group("full")}<!--/LINK:{slug}-->'
        t = li_re.sub(li_repl, t)
        # Pass 2: wrap remaining bare anchors. Need to re-check "already wrapped"
        # against the *updated* text.
        def a_repl(m):
            slug = m.group('slug')
            if slug == self_slug:
                return m.group('full')
            start = m.start()
            # Look behind for an unmatched <!--LINK:slug--> marker
            preceding = t[max(0, start - 80):start]
            last_open = preceding.rfind(f'<!--LINK:{slug}-->')
            last_close = preceding.rfind(f'<!--/LINK:{slug}-->')
            if last_open > last_close:
                return m.group('full')  # already wrapped
            return f'<!--LINK:{slug}-->{m.group("full")}<!--/LINK:{slug}-->'
        t = a_re.sub(a_repl, t)
        if t != original:
            f.write_text(t)
            changed_files += 1
            if verbose:
                print(f'  wrapped links in: {f.relative_to(ROOT)}')
    if verbose and changed_files == 0:
        print('  no unwrapped cross-blog links found')
    return changed_files


def sync_links(verbose=True):
    """Walk every blog file and update cross-blog link visibility."""
    published = {s for s in BLOGS if is_published(s)}
    changed_files = 0
    for f in sorted(BLOG_DIR.glob('*.html')):
        t = f.read_text()
        def repl(m):
            new_body = _transform_block(m.group('slug'), m.group('body'), published)
            return f'<!--LINK:{m.group("slug")}-->{new_body}<!--/LINK:{m.group("slug")}-->'
        new = LINK_BLOCK_RE.sub(repl, t)
        if new != t:
            f.write_text(new)
            changed_files += 1
            if verbose:
                print(f'  synced links in: {f.relative_to(ROOT)}')
    if verbose and changed_files == 0:
        print('  links already in sync')
    return changed_files

# ----------------------------------------------------------------------------

def publish(slug):
    if slug not in BLOGS:
        print(f'Unknown slug: {slug}')
        print(f'Valid slugs: {", ".join(BLOGS.keys())}')
        return 1
    print(f'Publishing {slug}...')
    r1 = publish_post_file(slug);       print(f'  noindex removed:       {"yes" if r1 else "already removed"}')
    r2 = publish_card_in_index(slug);   print(f'  card un-hidden:        {"yes" if r2 else "already visible"}')
    r3 = add_blogposting_jsonld(slug);  print(f'  JSON-LD entry added:   {"yes" if r3 else "already present"}')
    r4 = add_to_sitemap(slug);          print(f'  sitemap entry added:   {"yes" if r4 else "already present"}')
    print('  syncing cross-blog links:')
    sync_links()
    print('Done. Commit and push to publish live.')
    return 0

def unpublish(slug):
    if slug not in BLOGS:
        print(f'Unknown slug: {slug}')
        return 1
    print(f'Unpublishing {slug}...')
    r1 = unpublish_post_file(slug);     print(f'  noindex added:         {"yes" if r1 else "already present"}')
    r2 = unpublish_card_in_index(slug); print(f'  card hidden:           {"yes" if r2 else "already hidden"}')
    r3 = remove_blogposting_jsonld(slug); print(f'  JSON-LD entry removed: {"yes" if r3 else "not present"}')
    r4 = remove_from_sitemap(slug);     print(f'  sitemap entry removed: {"yes" if r4 else "not present"}')
    print('  syncing cross-blog links:')
    sync_links()
    print('Done.')
    return 0

# ----------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    if args[0] == '--list':
        list_status()
        return 0
    if args[0] == '--sync-links':
        print('Syncing cross-blog links across all blog files:')
        sync_links()
        return 0
    if args[0] == '--wrap-links':
        print('Wrapping unmarked cross-blog links across all blog files:')
        wrap_links()
        print('Syncing cross-blog links:')
        sync_links()
        return 0
    if args[0] == '--unpublish':
        if len(args) < 2:
            print('Usage: ./publish.py --unpublish <slug>')
            return 1
        return unpublish(args[1])
    return publish(args[0])

if __name__ == '__main__':
    sys.exit(main())
