#!/usr/bin/env python3
"""
Student Stash — Offer Page Generator

Generates docs/offers/<slug>.html — one real, pre-rendered page per offer,
linked from every offer row/card across the site instead of jumping
straight to the external provider.

What these pages intentionally do NOT include: step-by-step "how to apply"
instructions. Our source data is a one-line benefit description per offer,
not verified redemption steps — invented instructions at this scale (500+
providers, each with a different process) would be a real accuracy risk.
Instead, the page shows everything we actually know, cleanly, and points
people to the official page as the authoritative next step.

Because these are generated from docs/offers_data.json, they need to be
regenerated whenever that file changes — wired into
.github/workflows/update-site.yml to run after every data sync.

Usage:
    python3 scripts/generate_offer_pages.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    CAT_COLORS, CATEGORY_BLURBS, slugify, hex_to_rgb, extract_value, esc,
    favicon_domain, warn_badges_html, PAGE_TEMPLATE,
)

DATA_FILE = ROOT / "docs" / "offers_data.json"
OFFERS_DIR = ROOT / "docs" / "offers"

HEALTH_NOTES = {
    "dead": "The link returned an error on our last check — it may be down, or may have moved.",
    "unreachable": "We couldn't reach this link on our last check.",
    "timeout": "This link timed out on our last check.",
    "ssl_error": "This link had a certificate error on our last check.",
    "redirect": "This link redirected to a new address on our last check — the destination below reflects that.",
}


def big_favicon_html(url, name):
    domain = favicon_domain(url)
    initial = name.strip()[0].upper() if name.strip() else '?'
    if not domain:
        return initial
    src = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
    return (f'<img src="{src}" data-idx="0" data-domain="{domain}" '
            f'data-fallback="{initial}" onerror="handleImgError(this)" alt="">')


def related_row_html(o):
    domain = favicon_domain(o['url'])
    initial = o['name'].strip()[0].upper() if o['name'].strip() else '?'
    icon = (f'<img src="https://www.google.com/s2/favicons?sz=128&domain={domain}" '
            f'data-idx="0" data-domain="{domain}" data-fallback="{initial}" '
            f'onerror="handleImgError(this)" alt="">' if domain else initial)
    slug = o.get('slug') or slugify(o['name'])
    return f"""
      <a class="mini-row" href="/offers/{slug}">
        <div class="mini-favicon">{icon}</div>
        <span class="mini-name">{esc(o['name'])}</span>
        <span class="mini-ext">&rarr;</span>
      </a>"""


def generate_offer_page(o, related):
    color = CAT_COLORS.get(o['category_clean'], '#C8CCDB')
    rgb = hex_to_rgb(color)
    value = extract_value(o.get('benefit', ''))
    warn_badges = warn_badges_html(o)
    cat_slug = slugify(o['category_clean'])
    slug = o.get('slug') or slugify(o['name'])

    health_note = ""
    if o.get('link_health') in HEALTH_NOTES:
        health_note = f'<p class="offer-health-note">&#9888; {HEALTH_NOTES[o["link_health"]]}</p>'
    expired_note = ""
    if o.get('content_flag') == 'possibly_expired':
        phrase = o.get('content_flag_phrase', '')
        note = 'The page\'s own text suggested this offer may have ended'
        if phrase:
            note += f' (matched the phrase "{esc(phrase)}")'
        expired_note = f'<p class="offer-health-note">&#9888; {note} — worth double-checking before relying on it.</p>'

    related_html = "".join(related_row_html(r) for r in related)
    related_section = f"""
<div class="related-section">
  <h2>Other offers in {esc(o['category_clean'])}</h2>
  <div class="related-grid">{related_html}</div>
</div>""" if related else ""

    body = f"""
<header class="offer-hero">
  <div class="wrap">
    <div class="offer-hero-top">
      <div class="favicon" style="width:56px;height:56px;border-radius:14px;">{big_favicon_html(o['url'], o['name'])}</div>
      <div>
        <h1>{esc(o['name'])}</h1>
        <a class="offer-cat-link" href="/categories/{cat_slug}"><span class="dot" style="background:{color}"></span>{esc(o['category_clean'])}</a>
      </div>
    </div>
    <div class="offer-badges">
      {f'<span class="value-chip" style="--glow-rgb:{rgb};">{value}</span>' if value else ''}
      {warn_badges}
    </div>
    <p class="offer-benefit">{esc(o.get('benefit',''))}</p>
    {health_note}
    {expired_note}
    <div class="offer-cta-row">
      <a class="offer-cta" href="{o['url']}" target="_blank" rel="noopener">Get it — Visit official site &rarr;</a>
      <a class="nav-link-btn" href="/categories/{cat_slug}">See all {esc(o['category_clean'])} offers</a>
    </div>
    <p class="offer-disclaimer">This page shows what we know from our source data — we don't publish step-by-step application instructions, since redemption processes vary by provider and change often. Verify current eligibility and how to claim it on the official page above.</p>
  </div>
</header>
<main>
  <div class="wrap">
    {related_section}
  </div>
</main>
"""
    html = PAGE_TEMPLATE.format(
        title=f"{o['name']} Student Discount — Student Stash",
        description=(o.get('benefit', '') or f"{o['name']} student offer")[:155],
        css_path="/assets/style.css",
        home_path="/",
        index_path="/categories/",
        crumb=f'<p class="crumb"><a href="/">Home</a> / <a href="/categories/{cat_slug}">{esc(o["category_clean"])}</a> / {esc(o["name"])}</p>',
        category_name=esc(o['category_clean']),
        count=1,
        categories_list=esc(', '.join(sorted(CAT_COLORS.keys()))),
        body=body,
        js_path="/assets/site.js",
    )
    with open(OFFERS_DIR / f"{slug}.html", "w") as f:
        f.write(html)


def main():
    with open(DATA_FILE) as f:
        offers = json.load(f)

    missing_slugs = [o['name'] for o in offers if not o.get('slug')]
    if missing_slugs:
        print(f"WARNING: {len(missing_slugs)} offers have no slug and will be skipped "
              f"(run update_offers.py first, which assigns slugs): {missing_slugs[:5]}")

    OFFERS_DIR.mkdir(parents=True, exist_ok=True)

    by_category = {}
    for o in offers:
        by_category.setdefault(o['category_clean'], []).append(o)

    generated = 0
    for o in offers:
        if not o.get('slug'):
            continue
        same_cat = [x for x in by_category[o['category_clean']] if x is not o]
        related = same_cat[:6]
        generate_offer_page(o, related)
        generated += 1

    print(f"Generated {generated} offer pages in docs/offers/")


if __name__ == "__main__":
    main()
