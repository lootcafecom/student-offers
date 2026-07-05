# Student Stash

A self-updating index of student discounts and free tools, compiled from
open, community-maintained source lists.

## How it stays up to date

`docs/index.html` no longer has the offer data baked into it. At page load,
it fetches `docs/offers_data.json` and `docs/meta.json` over HTTP. That means
refreshing the data is just a matter of updating those two JSON files —
no HTML rebuild required.

A scheduled GitHub Action (`.github/workflows/update-site.yml`) does exactly
that, **every day**:

1. **`scripts/update_offers.py`** — re-fetches all seven source lists, parses
   each one's format, adds any genuinely new offers (by normalized name, so
   the same tool from two different sources doesn't get duplicated), and
   cross-checks developer-tool offers against GitHub Education's official
   current-partner list.
2. **`scripts/check_links.py`** — checks every offer's URL two different
   ways:
   - **HTTP status** — is the link itself alive, dead, or redirected.
   - **Content scan** — even a page returning 200 OK can describe an offer
     that's been discontinued (this happened for real during development:
     Bump.sh's own page said "no longer available in the GitHub Student
     Developer Pack" while the page itself loaded fine). The checker reads
     the first ~200KB of each page and scans for specific phrases like
     "this offer has ended" or "no longer part of the GitHub Student
     [Pack]", flagging matches as `content_flag: "possibly_expired"`
     alongside the exact phrase it matched, so you can see why it was
     flagged rather than just take it on faith.
3. Cards on the live site show a small warning badge if a link is down or
   possibly expired, straight from these fields — nothing is silently
   removed.
4. If either step changed the data, the workflow commits
   `docs/offers_data.json` and `docs/meta.json` straight to the repo.

Why daily is fine cost-wise: GitHub Actions on a public repo has no
meaningful minute limit, and even on a private repo the free tier (2,000
min/month) comfortably covers 30 runs of a few minutes each. The workflow
only pushes a commit when something actually changed, so off-days are
silent, not noisy.

### Honest limitations of the expiration check

- **It's a heuristic, not a certainty.** The phrase list catches common
  ways sites word a discontinued offer, but not every possible wording —
  treat a flag as "worth a human glance," not gospel.
- **It can't see JavaScript-rendered content.** The checker fetches raw
  HTML; on modern single-page-app sites, the actual visible text (including
  any "this offer has ended" banner) is often injected by client-side JS
  after load, which a plain HTTP GET never executes. For those sites this
  check will effectively always come back clean, even if the offer is
  actually dead. The only way to catch that reliably is a headless browser
  (e.g. Playwright) that actually renders the page — meaningfully heavier
  and slower to run daily across hundreds of sites, so it isn't included
  here, but it's the natural next upgrade if false negatives on JS-heavy
  sites turn out to matter to you.
- **False positives happen too** — e.g. a page that mentions "expired" in
  an unrelated context (a blog post, a cookie notice). That's why entries
  are flagged for review, not auto-deleted.

## One-time setup

1. Create a new GitHub repo and push these files to it.
2. **Settings → Pages** → Source: `Deploy from a branch` → Branch: `main`,
   folder: `/docs`. Save. Your site will be live at
   `https://<you>.github.io/<repo>/` within a minute or two.
3. **Settings → Actions → General** → confirm "Actions permissions" allows
   workflows to run (default is usually fine).
4. **Settings → Actions → General → Workflow permissions** → set to
   "Read and write permissions" — the workflow needs this to commit the
   data updates back to the repo.

That's it. No API keys or secrets are needed — everything here uses public,
unauthenticated data.

## Running it yourself, locally

```bash
pip install requests --break-system-packages
python3 scripts/update_offers.py   # pulls in new offers from all sources
python3 scripts/check_links.py     # checks every link is still alive
```

To preview the site locally (plain `file://` won't work — browsers block
`fetch()` of local files):

```bash
cd docs
python3 -m http.server 8000
# open http://localhost:8000
```

## Adding a new source list

Open `scripts/update_offers.py` and add an entry to the `SOURCES` list at
the top:

```python
{
    "name": "someone/some-list",
    "url": "https://raw.githubusercontent.com/someone/some-list/main/README.md",
    "parser": "bullet_list",  # or: pipe_table_link_first, rich_table, plain_url_table
},
```

Pick whichever of the four existing parsers matches that list's markdown
format (look at the raw README to tell which). If it uses a genuinely new
format, add a new parser function next to the others in the same file.

## Category pages

Alongside the main `docs/index.html`, there's now `docs/categories/` — a
real, pre-rendered page per category (`developer-tools.html`,
`cloud-hosting.html`, etc.) plus a `categories/index.html` directory linking
to all of them. Unlike the main site, these pages render their cards
directly into the HTML at build time rather than fetching JSON — better for
sharing a direct link to one category, and better for search engines, since
there's real crawlable content on load rather than an empty shell waiting
on JavaScript.

These regenerate automatically as part of the same daily workflow
(`scripts/generate_category_pages.py` runs after the data sync + link
check), so they stay in sync with `docs/offers_data.json` without any
manual step. If you ever change the site's visual design, update the CSS
in `docs/assets/style.css` — both the main page and every category page
read from that one shared file.

Country pages were considered and intentionally skipped: most of these 467
offers are global (verified by student email, not gated by country), so a
per-country split would mean guessing region data for entries that don't
actually have it. If real geographic data becomes available for a
meaningful chunk of offers later, this is worth revisiting.



- This only re-syncs the **open, static GitHub source lists** already wired
  up — it does not (and structurally can't, without a different approach)
  reach into gated platforms like UNiDAYS or Student Beans, which are
  account-gated and JS-rendered rather than plain files.
- The source lists themselves overlap heavily — expect diminishing returns
  from adding more of the same kind of list (see the categories/counts in
  `docs/meta.json` over time to track this).
- `check_links.py` flags dead links, it doesn't silently delete them —
  some "dead" results are false positives from bot-blocking, so a quick
  human glance at flagged entries before trusting the flag is worthwhile.
