#!/usr/bin/env python3
"""
Student Stash — Link Health Check

Checks every offer URL two different ways, because they catch different
failure modes:

  1. HTTP status — is the URL itself alive, dead, or redirected.
  2. Page content — even a "200 OK" page can describe an offer that's been
     discontinued (e.g. Bump.sh's own page said "no longer available in the
     GitHub Student Developer Pack" while still returning 200). This scans
     the fetched body for common expiration phrasing.

Both are heuristics, not certainties — see the honest limitations note in
README.md, especially around JavaScript-rendered pages.

Usage:
    pip install requests --break-system-packages
    python3 scripts/check_links.py

Runs automatically (daily) via .github/workflows/update-site.yml
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("Missing dependency. Install with: pip install requests --break-system-packages")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "docs" / "offers_data.json"
META_FILE = ROOT / "docs" / "meta.json"

TIMEOUT = 12
MAX_WORKERS = 10
MAX_BODY_BYTES = 200_000  # cap how much of the page we read, for speed
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

# Phrases that suggest the OFFER (not just the page) is dead. Deliberately
# specific — avoids generic words like "expired" or "sold out" alone, which
# false-positive on unrelated page content (a cookie banner, an unrelated
# product, etc).
EXPIRATION_PHRASES = [
    "no longer available",
    "no longer offer",
    "no longer part of the github student",
    "left the github student developer pack",
    "this offer has ended",
    "this offer has expired",
    "this promotion has ended",
    "this deal is no longer active",
    "offer is no longer valid",
    "program has ended",
    "program has been discontinued",
    "we've discontinued",
    "we have discontinued",
    "this benefit is no longer",
]


def scan_content_for_expiration(body_text):
    lowered = body_text.lower()
    for phrase in EXPIRATION_PHRASES:
        if phrase in lowered:
            return phrase
    return None


def check_url(offer):
    url = offer["url"]
    result = {"link_health": "error", "content_flag": None, "content_flag_phrase": None}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True, stream=True)
        # Read a capped amount of the body so we can scan text without
        # downloading arbitrarily large pages.
        raw = b""
        for chunk in resp.iter_content(chunk_size=8192):
            raw += chunk
            if len(raw) >= MAX_BODY_BYTES:
                break
        body_text = raw.decode(resp.encoding or "utf-8", errors="ignore")

        if resp.status_code >= 400:
            result["link_health"] = "dead"
        elif resp.status_code >= 300:
            result["link_health"] = "redirect"
        else:
            result["link_health"] = "ok"

        phrase = scan_content_for_expiration(body_text)
        if phrase:
            result["content_flag"] = "possibly_expired"
            result["content_flag_phrase"] = phrase

    except requests.exceptions.SSLError:
        result["link_health"] = "ssl_error"
    except requests.exceptions.ConnectionError:
        result["link_health"] = "unreachable"
    except requests.exceptions.Timeout:
        result["link_health"] = "timeout"
    except Exception:
        result["link_health"] = "error"
    return result


def main():
    with open(DATA_FILE) as f:
        offers = json.load(f)

    print(f"Checking {len(offers)} offer links (status + content scan)...")
    now = datetime.now(timezone.utc).isoformat()

    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(check_url, o): o["name"] for o in offers}
        done = 0
        for future in as_completed(futures):
            name = futures[future]
            r = future.result()
            results[name] = r
            done += 1
            flag = " [POSSIBLY EXPIRED: \"" + r["content_flag_phrase"] + "\"]" if r["content_flag"] else ""
            print(f"[{done}/{len(offers)}] {name}: {r['link_health']}{flag}")

    counts = {"ok": 0, "redirect": 0, "dead": 0, "unreachable": 0, "timeout": 0, "ssl_error": 0, "error": 0}
    possibly_expired = []
    for o in offers:
        r = results.get(o["name"], {"link_health": "error", "content_flag": None, "content_flag_phrase": None})
        o["link_health"] = r["link_health"]
        o["content_flag"] = r["content_flag"]
        o["content_flag_phrase"] = r["content_flag_phrase"]
        o["link_checked_at"] = now
        counts[r["link_health"]] = counts.get(r["link_health"], 0) + 1
        if r["content_flag"] == "possibly_expired":
            possibly_expired.append({"name": o["name"], "url": o["url"], "phrase": r["content_flag_phrase"]})

    with open(DATA_FILE, "w") as f:
        json.dump(offers, f, indent=2)

    meta = {}
    if META_FILE.exists():
        with open(META_FILE) as f:
            meta = json.load(f)
    meta.update({
        "last_link_check": now,
        "link_health_summary": counts,
        "possibly_expired_count": len(possibly_expired),
        "possibly_expired": possibly_expired,
    })
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)

    print("\n" + "=" * 40)
    print("LINK STATUS SUMMARY")
    print("=" * 40)
    for k, v in counts.items():
        print(f"  {k}: {v}")

    needs_review = [o["name"] for o in offers if o["link_health"] in ("dead", "unreachable", "ssl_error", "timeout")]
    if needs_review:
        print(f"\n{len(needs_review)} offers flagged DEAD/UNREACHABLE for manual review:")
        for name in needs_review:
            print(f"  - {name}")

    if possibly_expired:
        print(f"\n{len(possibly_expired)} offers flagged POSSIBLY EXPIRED (page loads fine, but content suggests the offer ended):")
        for item in possibly_expired:
            print(f"  - {item['name']}: matched \"{item['phrase']}\" — {item['url']}")


if __name__ == "__main__":
    main()

