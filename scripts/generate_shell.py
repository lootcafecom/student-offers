import json

# Curated "jewel tone" palette — distinct hues, similar lightness/saturation so they cohere as a family
cat_colors = {
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

colors_json = json.dumps(cat_colors, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Student Stash — Every Student Offer, In One Place</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="top-strip"></div>

<nav class="navbar">
  <div class="wrap">
    <a class="brand" href="/"><span class="mark">S</span>Student Stash</a>
    <div class="nav-right">
      <a href="/categories/" class="nav-link-btn"><span class="full">Browse by </span>category</a>
      <div class="nav-badge" id="nav-count">Loading…</div>
      <button class="theme-toggle" id="theme-toggle" aria-label="Toggle light/dark mode" title="Toggle light/dark mode">🌙</button>
    </div>
  </div>
</nav>
<div class="wrap" id="updated-row" style="display:none; padding-top:8px;">
  <span style="font-family:'Fira Code',monospace; font-size:11px; color:var(--text-faint);" id="updated-text"></span>
</div>

<header class="hero">
  <div class="wrap">
    <p class="eyebrow" id="eyebrow">Loading Student Offers · One Page</p>
    <h1>Every discount your <span class="grad">.edu status</span> already earned you.</h1>
    <p class="sub">A searchable index of software credits, cloud plans, learning platforms, and everyday discounts — compiled from open, community-maintained sources.</p>
    <div class="search-wrap">
      <input id="search" type="text" placeholder="Search by tool, brand, or category...">
    </div>
    <div class="hero-stats">
      <span><b id="count-total">…</b> offers</span>
      <span>&middot;</span>
      <span><b id="count-cats">…</b> categories</span>
    </div>
  </div>
</header>

<main>
  <div class="wrap">
    <div id="browse-view"></div>
    <div id="search-view" style="display:none;">
      <div class="search-view-head">
        <span><b id="count-results">…</b> results</span>
        <select id="sort">
          <option value="name">Sort: Name (A–Z)</option>
          <option value="category">Sort: Category</option>
        </select>
      </div>
      <div class="row-list" id="grid"></div>
    </div>
  </div>
</main>

<footer>
  <div class="wrap">
    <div class="foot-brand"><span class="mark">S</span>Student Stash</div>
    <p class="foot-tagline">A searchable index of student discounts and free tools, compiled from open, community-maintained sources.</p>
    <div class="foot-grid">
      <div>
        <span class="foot-title">About this index</span>
        <p>Student Stash indexes free tools, cloud credits, software licenses, and everyday discounts available to students. Every card links directly to the provider — verify eligibility and current terms there, since offers change often.</p>
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
        <p id="cat-list-foot"></p>
      </div>
    </div>
    <div class="foot-bottom">
      <span>Compiled from open-source, MIT-licensed community lists. Not affiliated with any provider listed. Prototype build.</span>
      <a href="#">&uarr; Back to top</a>
    </div>
  </div>
</footer>

<script>
let OFFERS = [];
const CAT_COLORS = __COLORS_JSON__;
let CATEGORIES = [];
let COUNTS = {};
let TOTAL = 0;
let query = '';
let sortMode = 'name';

async function loadData() {
  try {
    const offersRes = await fetch('offers_data.json', {cache: 'no-store'});
    if (!offersRes.ok) throw new Error('offers_data.json returned ' + offersRes.status);
    OFFERS = await offersRes.json();
    TOTAL = OFFERS.length;

    const counts = {};
    OFFERS.forEach(o => counts[o.category_clean] = (counts[o.category_clean]||0) + 1);
    CATEGORIES = Object.keys(counts).sort((a,b) => counts[b]-counts[a]);
    COUNTS = counts;

    document.getElementById('nav-count').textContent = TOTAL + ' offers';
    document.getElementById('eyebrow').textContent = TOTAL + '+ Student Offers · One Page';
    document.getElementById('count-total').textContent = TOTAL;
    document.getElementById('count-cats').textContent = CATEGORIES.length;
    document.getElementById('cat-list-foot').textContent = CATEGORIES.join(', ');

    try {
      const metaRes = await fetch('meta.json', {cache: 'no-store'});
      if (metaRes.ok) {
        const meta = await metaRes.json();
        const ts = meta.last_source_sync || meta.last_link_check;
        if (ts) {
          const d = new Date(ts);
          document.getElementById('updated-text').textContent = 'Data last synced ' + d.toLocaleDateString(undefined, {year:'numeric', month:'short', day:'numeric'});
          document.getElementById('updated-row').style.display = 'block';
        }
      }
    } catch (e) { /* meta.json is optional — don't block the page on it */ }

    renderCategoryGrid();
  } catch (e) {
    document.getElementById('nav-count').textContent = 'Error';
    document.getElementById('grid').innerHTML =
      '<div class="empty-state">Couldn\\'t load offers_data.json.<br><br>' +
      'If you just opened this file directly from your computer, that\\'s why — browsers block fetch() of local files opened via file://.<br>' +
      'Serve it over http/https instead (e.g. GitHub Pages, or run <code>python3 -m http.server</code> in this folder and open localhost).</div>';
  }
}

function hexToRgb(hex) {
  const h = hex.replace('#','');
  const r = parseInt(h.substring(0,2),16), g = parseInt(h.substring(2,4),16), b = parseInt(h.substring(4,6),16);
  return `${r},${g},${b}`;
}

function slugify(name) {
  return name.toLowerCase().replace(/[^\\w\\s-]/g, '').trim().replace(/[\\s_]+/g, '-');
}

function rowHtml(o, idx) {
  const color = CAT_COLORS[o.category_clean] || '#C8CCDB';
  const rgb = hexToRgb(color);
  const domain = faviconDomain(o.url);
  const value = extractValue(o.benefit);
  const initial = o.name.trim().charAt(0).toUpperCase();
  const candidates = domain ? faviconCandidates(domain) : [];
  const iconHtml = candidates.length
    ? `<img src="${candidates[0]}" data-idx="0" data-domain="${domain}" data-fallback="${initial}" onerror="handleImgError(this)" alt="">`
    : initial;
  const rankHtml = (idx !== undefined && idx !== null) ? `<span class="row-rank">${idx + 1}</span>` : '';
  const href = o.slug ? `/offers/${o.slug}` : o.url;
  return `
    <a class="offer-row" style="--glow-rgb: ${rgb};" href="${href}">
      ${rankHtml}
      <div class="favicon">${iconHtml}</div>
      <div class="row-main">
        <span class="row-name">${escapeHtml(o.name)}
          ${o.link_health && ['dead','unreachable','ssl_error','timeout'].includes(o.link_health) ? '<span class="warn-badge">LINK MAY BE DOWN</span>' : ''}
          ${o.content_flag === 'possibly_expired' ? '<span class="warn-badge">OFFER MAY HAVE ENDED</span>' : ''}
        </span>
        <span class="row-benefit">${escapeHtml(o.benefit)}</span>
      </div>
      <span class="row-tag"><span class="dot" style="background:${color}"></span>${o.category_clean}</span>
      <div class="row-right">
        <span class="value-chip ${value ? '' : 'empty'}">${value || '—'}</span>
        <span class="row-visit">Details &rarr;</span>
      </div>
    </a>
  `;
}


function miniRowHtml(o, idx) {
  const domain = faviconDomain(o.url);
  const initial = o.name.trim().charAt(0).toUpperCase();
  const candidates = domain ? faviconCandidates(domain) : [];
  const iconHtml = candidates.length
    ? `<img src="${candidates[0]}" data-idx="0" data-domain="${domain}" data-fallback="${initial}" onerror="handleImgError(this)" alt="">`
    : initial;
  const href = o.slug ? `/offers/${o.slug}` : o.url;
  return `
    <a class="mini-row" href="${href}">
      <span class="mini-rank">${idx + 1}.</span>
      <div class="mini-favicon">${iconHtml}</div>
      <span class="mini-name">${escapeHtml(o.name)}</span>
      <span class="mini-ext">&rarr;</span>
    </a>
  `;
}

function renderCategoryGrid() {
  const container = document.getElementById('browse-view');
  container.innerHTML = `<div class="cat-grid">` + CATEGORIES.map(name => {
    const color = CAT_COLORS[name] || '#C8CCDB';
    const inCat = OFFERS.filter(o => o.category_clean === name).sort((a,b) => a.name.localeCompare(b.name));
    const preview = inCat.slice(0, 10);
    return `
      <div class="cat-grid-card">
        <div class="cat-grid-head" style="border-bottom-color:${color}">
          <h3><span class="dot" style="background:${color}"></span>${name}</h3>
        </div>
        <div class="cat-grid-list">${preview.map((o, i) => miniRowHtml(o, i)).join('')}</div>
        <a class="cat-grid-see-all" href="/categories/${slugify(name)}">See all category (${COUNTS[name]}) &rarr;</a>
      </div>
    `;
  }).join('') + `</div>`;
}

function extractValue(text) {
  if (!text) return null;
  let m = text.match(/\\$[\\d,]+K?\\+?/i);
  if (m) return m[0].toUpperCase();
  m = text.match(/(\\d{1,3})\\s?%/);
  if (m) return m[0] + ' OFF';
  m = text.match(/(\\d+)\\s*(months?|years?|yrs?)\\b/i);
  if (m) return m[0].replace(/\\s+/g,' ').toUpperCase();
  if (/\\bfree\\b/i.test(text)) return 'FREE';
  return null;
}

function faviconCandidates(domain) {
  return [
    `https://www.google.com/s2/favicons?sz=128&domain=${domain}`,
    `https://icons.duckduckgo.com/ip3/${domain}.ico`,
  ];
}
function handleImgError(img) {
  const idx = parseInt(img.dataset.idx, 10) + 1;
  const domain = img.dataset.domain;
  const candidates = faviconCandidates(domain);
  if (idx < candidates.length) { img.dataset.idx = idx; img.src = candidates[idx]; }
  else { img.style.display = 'none'; img.parentElement.textContent = img.dataset.fallback; }
}
window.handleImgError = handleImgError;

function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  document.getElementById('theme-toggle').textContent = saved === 'dark' ? '☀️' : '🌙';
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('theme-toggle').textContent = next === 'dark' ? '☀️' : '🌙';
}
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
initTheme();
function faviconDomain(url) { try { return new URL(url).hostname; } catch(e) { return null; } }
function escapeHtml(str) { const div = document.createElement('div'); div.textContent = str; return div.innerHTML; }

function renderGrid() {
  const browseView = document.getElementById('browse-view');
  const searchView = document.getElementById('search-view');

  if (!query.trim()) {
    browseView.style.display = '';
    searchView.style.display = 'none';
    return;
  }
  browseView.style.display = 'none';
  searchView.style.display = 'block';

  const q = query.trim().toLowerCase();
  let filtered = OFFERS.filter(o => {
    const hay = (o.name + ' ' + o.benefit + ' ' + o.category_clean + ' ' + o.category).toLowerCase();
    return hay.includes(q);
  });

  filtered.sort((a,b) => {
    if (sortMode === 'category') {
      const c = a.category_clean.localeCompare(b.category_clean);
      return c !== 0 ? c : a.name.localeCompare(b.name);
    }
    return a.name.localeCompare(b.name);
  });

  document.getElementById('count-results').textContent = filtered.length;

  const grid = document.getElementById('grid');
  if (filtered.length === 0) {
    grid.innerHTML = `<div class="empty-state">No matches — try a different search term, or <a href="/categories/" style="color:#8C9EFF;">browse by category</a> instead.</div>`;
    return;
  }
  grid.innerHTML = filtered.map(o => rowHtml(o)).join('');
}

document.getElementById('search').addEventListener('input', (e) => { query = e.target.value; renderGrid(); });
document.getElementById('sort').addEventListener('change', (e) => { sortMode = e.target.value; renderGrid(); });

loadData();
</script>
</body>
</html>
"""

html = html.replace('__COLORS_JSON__', colors_json)

with open('/home/claude/repo/docs/index.html', 'w') as f:
    f.write(html)

print("Written", len(html), "bytes")
