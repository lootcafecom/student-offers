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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    CAT_COLORS, CATEGORY_BLURBS, slugify, hex_to_rgb, extract_value, esc,
    favicon_html, warn_badges_html, PAGE_TEMPLATE,
)

DATA_FILE = ROOT / "docs" / "offers_data.json"
CATEGORIES_DIR = ROOT / "docs" / "categories"


def render_row(o, idx=None):
    color = CAT_COLORS.get(o['category_clean'], '#C8CCDB')
    rgb = hex_to_rgb(color)
    value = extract_value(o.get('benefit', ''))
    icon_html = favicon_html(o['url'], o['name'])
    warn_badges = warn_badges_html(o)
    rank_html = f'<span class="row-rank">{idx + 1}</span>' if idx is not None else ''
    offer_slug = o.get('slug') or slugify(o['name'])

    return f"""
      <a class="offer-row" style="--glow-rgb: {rgb};" href="/offers/{offer_slug}" data-search="{esc((o['name'] + ' ' + o.get('benefit','')).lower())}">
        {rank_html}
        <div class="favicon">{icon_html}</div>
        <div class="row-main">
          <span class="row-name">{esc(o['name'])}
            {warn_badges}
          </span>
          <span class="row-benefit">{esc(o.get('benefit',''))}</span>
        </div>
        <span class="row-tag"><span class="dot" style="background:{color}"></span>{esc(o['category_clean'])}</span>
        <div class="row-right">
          <span class="value-chip {'empty' if not value else ''}">{value or '—'}</span>
          <span class="row-visit">Details &rarr;</span>
        </div>
      </a>"""



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
    with open(CATEGORIES_DIR / f"{slug}.html", "w") as f:
        f.write(html)
    return slug


def generate_categories_index(category_counts):
    cards = ""
    for name, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        slug = slugify(name)
        color = CAT_COLORS.get(name, '#C8CCDB')
        blurb = CATEGORY_BLURBS.get(name, '')
        cards += f"""
      <a class="cat-list-card" href="/categories/{slug}">
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
