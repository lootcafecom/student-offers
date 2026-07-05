#!/usr/bin/env python3
"""
Student Stash — Category Page Generator

Generates docs/categories/<slug>.html (one real, pre-rendered page per
category) plus docs/categories/index.html (a directory of all categories).

Unlike docs/index.html, these pages render their offer cards directly into
the HTML at build time rather than fetching JSON client-side — better for
SEO and for anyone sharing a direct link to "Cloud & Hosting offers" rather
than the whole site.

Because these are generated from docs/offers_data.json, they need to be
regenerated whenever that file changes — this script is wired into
.github/workflows/update-site.yml to run automatically after every data
sync, so these pages never go stale.

Usage:
    python3 scripts/generate_category_pages.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "docs" / "offers_data.json"
CATEGORIES_DIR = ROOT / "docs" / "categories"

CAT_COLORS = {
    'Developer Tools': '#4FC3F7',
    'Cloud & Hosting': '#4FA8E8',
    'Learning & Courses': '#FFC857',
    'Productivity': '#B388FF',
    'Design & Creative': '#FF6FA8',
    'Shopping': '#FF9E5E',
    'Entertainment': '#FF6B81',
    'Travel & Shipping': '#7EA6FF',
    'Security & Analytics': '#B0B8D9',
    'Data & AI': '#8C9EFF',
    'Marketing & Social': '#FF7BD1',
    'ID Cards & Bundles': '#FFD54F',
    'Mobile & IoT': '#FFAB91',
    'Institutional (Faculty-Only)': '#FF8A80',
    'Other': '#C8CCDB',
}

CATEGORY_BLURBS = {
    'Developer Tools': 'IDEs, version control, CI/CD, APIs, and everything else that goes into shipping code.',
    'Cloud & Hosting': 'Cloud credits, domains, VPS hosting, and infrastructure to run your own projects.',
    'Learning & Courses': 'Course platforms, certifications, and career resources at a student price — often free.',
    'Productivity': 'Note-taking, task management, password managers, and tools to keep projects organized.',
    'Design & Creative': 'Design, prototyping, 3D, and creative software with an education license.',
    'Shopping': 'Retail, electronics, and everyday discounts that just need a valid student ID.',
    'Entertainment': 'Streaming, music, and other everyday student perks.',
    'Travel & Shipping': 'Travel booking, shipping, and baggage discounts for students.',
    'Security & Analytics': 'Security tooling, monitoring, and analytics platforms with a student tier.',
    'Data & AI': 'Data science, machine learning, and AI platforms offering academic access.',
    'Marketing & Social': 'Marketing and social media tools with student pricing.',
    'ID Cards & Bundles': 'Bundled discount programs and ID-card-based savings networks.',
    'Mobile & IoT': 'Mobile development and IoT hardware/software discounts.',
    'Institutional (Faculty-Only)': 'Benefits that require your institution to register first, not just your own student status.',
    'Other': 'Everything else that did not cleanly fit another category.',
}


def slugify(name):
    s = re.sub(r'[^\w\s-]', '', name.lower())
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return s


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def extract_value(text):
    if not text:
        return None
    m = re.search(r'\$[\d,]+K?\+?', text, re.I)
    if m:
        return m.group(0).upper()
    m = re.search(r'(\d{1,3})\s?%', text)
    if m:
        return m.group(0) + ' OFF'
    m = re.search(r'(\d+)\s*(months?|years?|yrs?)\b', text, re.I)
    if m:
        return re.sub(r'\s+', ' ', m.group(0)).upper()
    if re.search(r'\bfree\b', text, re.I):
        return 'FREE'
    return None


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&#39;'))


def favicon_domain(url):
    m = re.match(r'https?://([^/]+)', url)
    return m.group(1) if m else None


def render_row(o, idx=None):
    color = CAT_COLORS.get(o['category_clean'], '#C8CCDB')
    rgb = hex_to_rgb(color)
    domain = favicon_domain(o['url'])
    value = extract_value(o.get('benefit', ''))
    initial = o['name'].strip()[0].upper() if o['name'].strip() else '?'
    candidates_first = f"https://www.google.com/s2/favicons?sz=128&domain={domain}" if domain else None
    icon_html = (
        f'<img src="{candidates_first}" data-idx="0" data-domain="{domain}" '
        f'data-fallback="{initial}" onerror="handleImgError(this)" alt="">'
        if candidates_first else initial
    )
    verified_badge = '<span class="verified-badge">GITHUB ED. PARTNER</span>' if o.get('pack_verified') else ''
    warn_badges = ''
    if o.get('link_health') in ('dead', 'unreachable', 'ssl_error', 'timeout'):
        warn_badges += '<span class="warn-badge">LINK MAY BE DOWN</span>'
    if o.get('content_flag') == 'possibly_expired':
        warn_badges += '<span class="warn-badge">OFFER MAY HAVE ENDED</span>'
    rank_html = f'<span class="row-rank">{idx + 1}</span>' if idx is not None else ''

    return f"""
      <a class="offer-row" style="--glow-rgb: {rgb};" href="{o['url']}" target="_blank" rel="noopener" data-search="{esc((o['name'] + ' ' + o.get('benefit','')).lower())}">
        {rank_html}
        <div class="favicon">{icon_html}</div>
        <div class="row-main">
          <span class="row-name">{esc(o['name'])}
            {verified_badge}
            {warn_badges}
          </span>
          <span class="row-benefit">{esc(o.get('benefit',''))}</span>
        </div>
        <span class="row-tag"><span class="dot" style="background:{color}"></span>{esc(o['category_clean'])}</span>
        <div class="row-right">
          <span class="value-chip {'empty' if not value else ''}">{value or '—'}</span>
          <span class="row-visit">Visit &rarr;</span>
        </div>
      </a>"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_path}">
</head>
<body>
<div class="top-strip"></div>
<nav class="navbar">
  <div class="wrap">
    <a class="brand" href="{home_path}"><span class="mark">S</span>Student Stash</a>
    <div class="nav-right">
      <a class="nav-link-btn" href="{index_path}"><span class="full">Browse by </span>category</a>
      <div class="nav-badge">{count} offers</div>
      <button class="theme-toggle" id="theme-toggle" aria-label="Toggle light/dark mode" title="Toggle light/dark mode">🌙</button>
    </div>
  </div>
</nav>
<div class="wrap">
  {crumb}
</div>
{body}
<footer>
  <div class="wrap">
    <div class="foot-brand"><span class="mark">S</span>Student Stash</div>
    <p class="foot-tagline">A searchable index of student discounts and free tools, compiled from open, community-maintained sources.</p>
    <div class="foot-grid">
      <div>
        <span class="foot-title">About this index</span>
        <p>Student Stash indexes free tools, cloud credits, software licenses, and everyday discounts available to students. Every entry links directly to the provider — verify eligibility and current terms there, since offers change often. Entries marked <b>GitHub Ed. Partner</b> were cross-checked against GitHub Education's official current-partner list.</p>
      </div>
      <div>
        <span class="foot-title">Data sources</span>
        <ul>
          <li><a class="src" href="https://github.com/ShreyamMaity/student-offers" target="_blank" rel="noopener">ShreyamMaity/student-offers ↗</a></li>
          <li><a class="src" href="https://github.com/AchoArnold/discount-for-student-dev" target="_blank" rel="noopener">AchoArnold/discount-for-student-dev ↗</a></li>
          <li><a class="src" href="https://github.com/OpenGenus/Best-student-discount-services" target="_blank" rel="noopener">OpenGenus/Best-student-discount-services ↗</a></li>
          <li><a class="src" href="https://github.com/couponswift/awesome-student-software-deals" target="_blank" rel="noopener">couponswift/awesome-student-software-deals ↗</a></li>
          <li><a class="src" href="https://github.com/jhaxce/student-perks" target="_blank" rel="noopener">jhaxce/student-perks ↗</a></li>
          <li><a class="src" href="https://github.com/github-education-resources/Student-Developer-Pack-Current-Partners-FAQ" target="_blank" rel="noopener">Official GitHub Education partner list ↗</a></li>
        </ul>
      </div>
      <div>
        <span class="foot-title">Categories</span>
        <p>{categories_list}</p>
      </div>
    </div>
    <div class="foot-bottom">
      <span>Compiled from open-source, MIT-licensed community lists. Not affiliated with any provider listed.</span>
      <a href="{home_path}">&uarr; Back to top</a>
    </div>
  </div>
</footer>
<script src="{js_path}"></script>
</body>
</html>
"""


def generate_category_page(category_name, offers_in_cat):
    slug = slugify(category_name)
    blurb = CATEGORY_BLURBS.get(category_name, '')
    rows_html = "\n".join(render_row(o, i) for i, o in enumerate(offers_in_cat))

    body = f"""
<header class="cat-hero">
  <div class="wrap">
    <h1>{esc(category_name)}</h1>
    <p class="count">{len(offers_in_cat)} offers &middot; {esc(blurb)}</p>
    <div class="cat-search">
      <input id="search" type="text" placeholder="Search within {esc(category_name)}...">
    </div>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="row-list" id="grid">{rows_html}
    </div>
  </div>
</main>
<script>
document.getElementById('search').addEventListener('input', (e) => {{
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('#grid .offer-row').forEach(row => {{
    row.style.display = row.dataset.search.includes(q) ? '' : 'none';
  }});
}});
</script>
"""
    # Absolute paths from domain root — avoids any dependency on relative
    # depth, trailing slashes, or host-specific redirect behavior (this was
    # the root cause of the broken-CSS / 404 issues with relative paths).
    html = PAGE_TEMPLATE.format(
        title=f"{category_name} Student Discounts — Student Stash",
        description=f"{len(offers_in_cat)} student discounts and free tools in {category_name}. {blurb}",
        css_path="/assets/style.css",
        home_path="/",
        index_path="/categories/",
        crumb=f'<p class="crumb"><a href="/">Home</a> / <a href="/categories/">Categories</a> / {esc(category_name)}</p>',
        category_name=esc(category_name),
        count=len(offers_in_cat),
        categories_list=esc(', '.join(sorted(CAT_COLORS.keys()))),
        body=body,
        js_path="/assets/site.js",
    )
    page_dir = CATEGORIES_DIR / slug
    page_dir.mkdir(parents=True, exist_ok=True)
    with open(page_dir / "index.html", "w") as f:
        f.write(html)
    return slug


def generate_categories_index(category_counts):
    cards = ""
    for name, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        slug = slugify(name)
        color = CAT_COLORS.get(name, '#C8CCDB')
        blurb = CATEGORY_BLURBS.get(name, '')
        cards += f"""
      <a class="cat-list-card" href="/categories/{slug}/">
        <h3><span class="dot" style="background:{color}"></span>{esc(name)}</h3>
        <p>{count} offers &middot; {esc(blurb)}</p>
      </a>"""

    total = sum(category_counts.values())
    body = f"""
<header class="cat-hero">
  <div class="wrap">
    <h1>Browse by category</h1>
    <p class="count">{total} offers across {len(category_counts)} categories</p>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="cat-list-grid">{cards}
    </div>
  </div>
</main>
"""
    html = PAGE_TEMPLATE.format(
        title="Browse Student Discounts by Category — Student Stash",
        description=f"Browse {total} student discounts and free tools across {len(category_counts)} categories.",
        css_path="/assets/style.css",
        home_path="/",
        index_path="/categories/",
        crumb='<p class="crumb"><a href="/">Home</a> / Categories</p>',
        category_name="Categories",
        count=total,
        categories_list=esc(', '.join(sorted(CAT_COLORS.keys()))),
        body=body,
        js_path="/assets/site.js",
    )
    with open(CATEGORIES_DIR / "index.html", "w") as f:
        f.write(html)


def main():
    with open(DATA_FILE) as f:
        offers = json.load(f)

    CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)

    by_category = {}
    for o in offers:
        by_category.setdefault(o['category_clean'], []).append(o)

    for name, items in by_category.items():
        items.sort(key=lambda o: o['name'].lower())
        slug = generate_category_page(name, items)
        print(f"  {name}: {len(items)} offers -> categories/{slug}.html")

    category_counts = {name: len(items) for name, items in by_category.items()}
    generate_categories_index(category_counts)
    print(f"\nGenerated {len(by_category)} category pages + categories/index.html")


if __name__ == "__main__":
    main()
