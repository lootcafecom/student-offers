#!/usr/bin/env python3
"""
Student Stash — Source Sync

Fetches every configured source list, parses each one (they use different
markdown formats), merges the results into docs/offers_data.json without
losing existing verification flags, re-categorizes everything, validates
URLs structurally, and cross-checks developer-tool offers against GitHub
Education's official current-partner list.

This script does NOT touch docs/index.html — the site loads its data at
runtime via fetch(), so updating docs/offers_data.json is enough to refresh
the live site (once served over http/https, e.g. GitHub Pages).

Usage:
    pip install requests --break-system-packages
    python3 scripts/update_offers.py

Runs automatically on a schedule via .github/workflows/update-site.yml
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Missing dependency. Install with: pip install requests --break-system-packages")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "docs" / "offers_data.json"
META_FILE = ROOT / "docs" / "meta.json"

HEADERS = {"User-Agent": "student-stash-sync/1.0 (+https://github.com/)"}
TIMEOUT = 15

# ---------------------------------------------------------------------------
# Source configuration
# Add a new source by adding one entry here — no other code changes needed
# as long as it uses one of the four parser formats below.
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "name": "ShreyamMaity/student-offers",
        "url": "https://raw.githubusercontent.com/ShreyamMaity/student-offers/main/README.md",
        "parser": "pipe_table_link_first",
    },
    {
        "name": "AchoArnold/discount-for-student-dev",
        "url": "https://raw.githubusercontent.com/AchoArnold/discount-for-student-dev/master/README.md",
        "parser": "bullet_list",
    },
    {
        "name": "OpenGenus/Best-student-discount-services",
        "url": "https://raw.githubusercontent.com/OpenGenus/Best-student-discount-services/master/README.md",
        "parser": "bullet_list",
    },
    {
        "name": "couponswift/awesome-student-software-deals",
        "url": "https://raw.githubusercontent.com/couponswift/awesome-student-software-deals/main/README.md",
        "parser": "bullet_list",
    },
    {
        "name": "jhaxce/student-perks",
        "url": "https://raw.githubusercontent.com/jhaxce/student-perks/main/README.md",
        "parser": "rich_table",
    },
    {
        "name": "Shashwat-19/awesome-student-resources",
        "url": "https://raw.githubusercontent.com/Shashwat-19/awesome-student-resources/main/README.md",
        "parser": "plain_url_table",
    },
    {
        "name": "Elele-Group/free-for-students",
        "url": "https://raw.githubusercontent.com/Elele-Group/free-for-students/main/README.md",
        "parser": "bullet_list",
    },
    {
        "name": "kamath/student-free-stuff",
        "url": "https://raw.githubusercontent.com/kamath/student-free-stuff/master/README.md",
        "parser": "bullet_list",
    },
    {
        "name": "Aashish-po/edu-email-benefits",
        "url": "https://raw.githubusercontent.com/Aashish-po/edu-email-benefits/main/README.md",
        "parser": "verification_table",
    },
]

OFFICIAL_PARTNERS_URL = "https://raw.githubusercontent.com/github-education-resources/Student-Developer-Pack-Current-Partners-FAQ/main/README.md"

CATEGORY_KEYWORDS = [
    ("Developer Tools", ["saas", "paas", "ci / cd", "ci/cd", "software pack", "softwares",
     "software licensing", "develop", "code", "repo", "ide", "version control", "devops",
     "api", "smtp", "email", "test", "website", "source code", "software & development"]),
    ("Cloud & Hosting", ["cloud", "hosting", "server", "infrastructure", "domain", "dns",
     "cpanel", "web & domains", "cloud services"]),
    ("Design & Creative", ["design", "art", "ui/ux", "3d", "render", "animation", "game", "prototype", "creative"]),
    ("Learning & Courses", ["learn", "education", "course", "certification", "career", "job search", "learning platform"]),
    ("Data & AI", ["data cleaner", "data analysis", "ai ml", "ai-powered", "ai &", "ai and",
     "ai tool", "database service", "data science", "machine learning"]),
    ("Shopping", ["shop", "product", "electronic", "apparel", "vehicle", "lens", "spectacle", "hardware"]),
    ("Entertainment", ["music", "video", "entertain", "newspaper", "streaming", "cinema", "meditation", "lifestyle"]),
    ("Productivity", ["productiv", "note", "password", "tool", "screen record", "visual analytics",
     "monitoring", "survey", "portfolio", "diagram", "project management", "business problem", "collaboration",
     "for all institutions"]),
    ("Security & Analytics", ["security", "analytic", "insurance", "cybersecurity", "privacy"]),
    ("Marketing & Social", ["market", "social"]),
    ("Mobile & IoT", ["mobile", "iot", "internet of things", "cellular"]),
    ("Food & Dining", ["food", "restaurant", "dining"]),
    ("Travel & Shipping", ["travel", "hotel", "flight", "shipping", "baggage"]),
    ("ID Cards & Bundles", ["collective discount", "card"]),
    ("Institutional (Faculty-Only)", ["institutional", "faculty"]),
]


def normalize_category(raw_category):
    c = raw_category.lower()
    for clean_name, keywords in CATEGORY_KEYWORDS:
        if any(k in c for k in keywords):
            return clean_name
    return "Other"


def norm_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def slugify(name):
    s = re.sub(r"[^\w\s-]", "", name.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s or "item"


def assign_slugs(offers):
    """Give every offer a stable, unique slug for its detail page URL.
    Offers that already have one keep it — slugs must never change once
    assigned, or previously-shared /offers/<slug> links would break."""
    used = {o["slug"] for o in offers if o.get("slug")}
    for o in offers:
        if o.get("slug"):
            continue
        base = slugify(o["name"])
        candidate = base
        n = 2
        while candidate in used:
            candidate = f"{base}-{n}"
            n += 1
        o["slug"] = candidate
        used.add(candidate)
    return offers


def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Parsers — one per markdown format seen across source repos
# ---------------------------------------------------------------------------

def parse_pipe_table_link_first(text, source_name):
    """Format: |[Name](url)|Benefit|Category|"""
    results = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("|[") or (line.startswith("|") and "](" in line):
            parts = [p.strip() for p in line.split("|") if p.strip() != ""]
            if len(parts) >= 3:
                m = re.match(r"\[(.*?)\]\((.*?)\)", parts[0])
                if m:
                    name, url = m.group(1), m.group(2)
                    if "ShreyamMaity/student-offers" in url:
                        continue  # skip broken placeholder links pointing back to the repo itself
                    results.append({
                        "name": name, "url": url,
                        "benefit": parts[1].replace("\\$", "$"),
                        "category": parts[2], "source": source_name,
                    })
    return results


def parse_bullet_list(text, source_name):
    """Format: * [Name](url) [TAG] - description, under ## Section headers"""
    results = []
    current_section = "Other"
    header_re = re.compile(r"^#{1,3}\s+(.+)$")
    bullet_re = re.compile(r"^\s*[\*\-]\s*\[([^\]]+)\]\(([^)]+)\)\s*(\[([A-Z /]+)\])?\s*[-:]?\s*(.*)$")
    for line in text.split("\n"):
        h = header_re.match(line)
        if h:
            title = re.sub(r"^[^\w]+", "", h.group(1).strip()).strip()
            if title.lower() not in ("table of contents", "contents", "contributing", "license", "note", "notes"):
                current_section = title
            continue
        b = bullet_re.match(line)
        if b:
            name, url, _, tag, desc = b.groups()
            name, url = name.strip(), url.strip()
            if url.startswith("#") or not url.startswith("http"):
                continue
            desc = desc.strip(" .")
            if tag:
                desc = f"[{tag.strip()}] {desc}" if desc else f"[{tag.strip()}]"
            if not desc:
                desc = "Student discount/benefit — see provider page for details."
            results.append({"name": name, "url": url, "benefit": desc, "category": current_section, "source": source_name})
    return results


def parse_rich_table(text, source_name):
    """Format: | **Name** | Description | Benefits | **Type** | Role/Req | [Link](url) |"""
    results = []
    current_section = "Other"
    header_re = re.compile(r"^#{1,3}\s+(.+)$")
    row_re = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|\s*\[Link\]\((.+?)\)\s*\|\s*$")
    for line in text.split("\n"):
        h = header_re.match(line)
        if h:
            title = re.sub(r"^[^\w]+", "", h.group(1).strip()).strip()
            if title.lower() not in ("categories", "contents"):
                current_section = title
            continue
        r = row_re.match(line)
        if r:
            name, desc, benefits, typ, role, url = r.groups()
            name = re.sub(r"\*\*", "", name).strip()
            benefit_text = f"{desc.strip()} — {benefits.strip()}" if desc.strip() else benefits.strip()
            if role.strip() and role.strip().lower() != "open to all":
                benefit_text += f" ({role.strip()})"
            results.append({"name": name, "url": url.strip(), "benefit": benefit_text, "category": current_section, "source": source_name})
    return results


def parse_plain_url_table(text, source_name):
    """Format: | **Name** | Benefit | https://plain-url |"""
    results = []
    current_section = "Other"
    header_re = re.compile(r"^#{1,3}\s+(.+)$")
    row_re = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|\s*(https?://\S+?)\s*\|\s*$")
    for line in text.split("\n"):
        h = header_re.match(line)
        if h:
            title = re.sub(r"^[^\w]+", "", h.group(1).strip()).strip()
            if title.lower() not in ("categories", "contents"):
                current_section = title
            continue
        r = row_re.match(line)
        if r:
            name, benefit, url = r.groups()
            name = re.sub(r"\*\*", "", name).strip()
            results.append({"name": name, "url": url.strip(), "benefit": benefit.strip(), "category": current_section, "source": source_name})
    return results


def parse_verification_table(text, source_name):
    """Format: | [Name](url) | emoji **Benefit** | Verification method | [-> Claim](link) |"""
    results = []
    current_section = "Other"
    header_re = re.compile(r"^#{1,4}\s+(.+)$")
    row_re = re.compile(r"^\|\s*\[(.+?)\]\((https?://[^)]+)\)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[.*?\]\((https?://[^)]+)\)\s*\|\s*$")
    for line in text.split("\n"):
        h = header_re.match(line)
        if h:
            title = re.sub(r"^[^\w]+", "", h.group(1).strip()).strip()
            if title.lower() not in ("service", "table of contents"):
                current_section = title
            continue
        r = row_re.match(line)
        if r:
            name, url, benefit, verification, _ = r.groups()
            benefit_clean = re.sub(r"[🟢🟡🟣🔵🟠🔴]", "", benefit).replace("**", "").strip()
            full_benefit = f"{benefit_clean} — {verification}".strip(" —")
            results.append({"name": name.strip(), "url": url.strip(), "benefit": full_benefit, "category": current_section, "source": source_name})
    return results


PARSERS = {
    "pipe_table_link_first": parse_pipe_table_link_first,
    "bullet_list": parse_bullet_list,
    "rich_table": parse_rich_table,
    "plain_url_table": parse_plain_url_table,
    "verification_table": parse_verification_table,
}


def fix_and_validate_url(url):
    """Returns a cleaned URL, or None if it should be dropped entirely."""
    if url in ("https://", "http://", ""):
        return None
    if url.startswith("https://https://") or url.startswith("http://http://"):
        url = re.sub(r"^https?://(https?://)", r"\1", url)
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc or "." not in p.netloc:
        return None
    if any(bad in url.lower() for bad in ["example.com", "localhost", "placeholder"]):
        return None
    return url


def parse_official_partners(text):
    """Returns (current_names_set, left_pack_names_set) from the official GitHub Education FAQ repo."""
    current, left = set(), set()
    row_re = re.compile(r"^\|\s*([^|]+?)\s*\|\s*\|\s*(.+?)\s*\|\s*$")
    for line in text.split("\n"):
        m = row_re.match(line)
        if m:
            name_field = m.group(1).strip()
            is_left = bool(re.search(r"left the pack", name_field, re.I))
            clean_name = re.sub(r"\(.*?\)", "", name_field).strip()
            (left if is_left else current).add(norm_name(clean_name))
    return current, left


def main():
    print(f"Student Stash sync — {datetime.now(timezone.utc).isoformat()}")

    # Load existing data (preserve manually-reviewed flags for entries we already know)
    existing = []
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            existing = json.load(f)
    existing_by_key = {norm_name(o["name"]): o for o in existing}
    print(f"Existing dataset: {len(existing)} offers")

    # Fetch + parse every source
    all_new = []
    for src in SOURCES:
        try:
            text = fetch(src["url"])
            parser = PARSERS[src["parser"]]
            parsed = parser(text, src["name"])
            print(f"  {src['name']}: fetched {len(parsed)} entries")
            all_new.extend(parsed)
        except Exception as e:
            print(f"  {src['name']}: FAILED ({e}) — skipping this source for this run")

    # Merge: keep existing entries as-is (preserves pack_verified / prior fixes),
    # add genuinely new ones by normalized name
    merged = dict(existing_by_key)
    added, dropped_broken = 0, 0
    for o in all_new:
        key = norm_name(o["name"])
        if key in merged:
            continue
        clean_url = fix_and_validate_url(o["url"])
        if not clean_url:
            dropped_broken += 1
            continue
        o["url"] = clean_url
        o["category_clean"] = normalize_category(o.get("category", "Other"))
        o.pop("source", None)
        merged[key] = o
        added += 1

    offers = list(merged.values())

    # Re-run structural validation + category normalization on EVERYTHING
    # (covers entries added in earlier manual sessions too)
    clean_offers = []
    for o in offers:
        clean_url = fix_and_validate_url(o["url"])
        if not clean_url:
            continue
        o["url"] = clean_url
        if "category_clean" not in o:
            o["category_clean"] = normalize_category(o.get("category", "Other"))
        clean_offers.append(o)
    offers = clean_offers

    # Cross-check against the official GitHub Education partner list
    try:
        official_text = fetch(OFFICIAL_PARTNERS_URL)
        official_current, official_left = parse_official_partners(official_text)
        verified_count = 0
        for o in offers:
            key = norm_name(o["name"])
            if key in official_current:
                o["pack_verified"] = True
                verified_count += 1
            elif key in official_left and "left the official GitHub Student Pack" not in o["benefit"]:
                o["benefit"] += " ⚠ Left the official GitHub Student Pack — verify current terms directly."
        print(f"Official partner cross-check: {verified_count} confirmed current")
    except Exception as e:
        print(f"Official partner list fetch FAILED ({e}) — skipping this cross-check for this run")

    offers = assign_slugs(offers)

    with open(DATA_FILE, "w") as f:
        json.dump(offers, f, indent=2)

    meta = {}
    if META_FILE.exists():
        with open(META_FILE) as f:
            meta = json.load(f)
    meta.update({
        "last_source_sync": datetime.now(timezone.utc).isoformat(),
        "total_offers": len(offers),
        "categories": sorted(set(o["category_clean"] for o in offers)),
        "pack_verified_count": sum(1 for o in offers if o.get("pack_verified")),
    })
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDone. {added} new offers added, {dropped_broken} broken links dropped.")
    print(f"Total: {len(offers)} offers -> {DATA_FILE}")


if __name__ == "__main__":
    main()
