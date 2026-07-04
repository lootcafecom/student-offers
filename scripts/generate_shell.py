import json

# Curated "jewel tone" palette — distinct hues, similar lightness/saturation so they cohere as a family
cat_colors = {
    'Developer Tools': '#4FC3F7',
    'Cloud & Hosting': '#4DD0B1',
    'Learning & Courses': '#FFC857',
    'Productivity': '#B388FF',
    'Design & Creative': '#FF6FA8',
    'Shopping': '#FF9E5E',
    'Entertainment': '#5EE6D0',
    'Travel & Shipping': '#7EA6FF',
    'Security & Analytics': '#B0B8D9',
    'Data & AI': '#8C9EFF',
    'Marketing & Social': '#FF7BD1',
    'ID Cards & Bundles': '#FFD54F',
    'Mobile & IoT': '#66E08A',
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
<style>
  :root {
    --bg: #0B0E1A;
    --bg-2: #0F1326;
    --card: #141830;
    --card-hover: #181D38;
    --text: #EEF0FA;
    --text-soft: rgba(238,240,250,0.66);
    --text-faint: rgba(238,240,250,0.40);
    --border: rgba(255,255,255,0.09);
    --verified: #66E08A;
    --verified-rgb: 102,224,138;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background:
      radial-gradient(ellipse 900px 500px at 15% -10%, rgba(140,158,255,0.16), transparent 60%),
      radial-gradient(ellipse 800px 500px at 100% 0%, rgba(255,158,94,0.10), transparent 60%),
      var(--bg);
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 0 32px; }
  a { color: inherit; }
  ::selection { background: rgba(140,158,255,0.35); }

  .navbar { position: sticky; top: 0; z-index: 30; backdrop-filter: blur(10px); background: rgba(11,14,26,0.78); border-bottom: 1px solid var(--border); }
  .navbar .wrap { display: flex; align-items: center; justify-content: space-between; height: 66px; }
  .brand { display: flex; align-items: center; gap: 10px; font-family: 'Sora', sans-serif; font-weight: 800; font-size: 18px; }
  .brand .mark { width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, #8C9EFF, #FF6FA8); box-shadow: 0 0 18px -2px rgba(140,158,255,0.7); display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; color: #0B0E1A; }
  .nav-badge { font-family: 'Fira Code', monospace; font-size: 12px; color: var(--text-soft); border: 1px solid var(--border); padding: 6px 12px; border-radius: 20px; }

  .hero { padding: 68px 0 44px; text-align: center; }
  .hero .eyebrow { font-family: 'Fira Code', monospace; font-size: 12.5px; letter-spacing: 2px; text-transform: uppercase; color: #8C9EFF; margin: 0 0 16px; }
  .hero h1 { font-family: 'Sora', sans-serif; font-weight: 800; font-size: clamp(32px, 5vw, 52px); line-height: 1.08; letter-spacing: -0.02em; margin: 0 auto 18px; max-width: 720px; }
  .hero h1 .grad { background: linear-gradient(90deg, #8C9EFF, #FF6FA8 60%, #FFC857); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .hero .sub { font-size: 16.5px; color: var(--text-soft); max-width: 520px; margin: 0 auto 30px; line-height: 1.6; }

  .search-wrap { max-width: 540px; margin: 0 auto 14px; position: relative; }
  .search-wrap input {
    width: 100%; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px;
    padding: 15px 20px; border-radius: 14px; border: 1px solid var(--border);
    background: var(--card); color: var(--text); outline: none;
  }
  .search-wrap input:focus { border-color: rgba(140,158,255,0.6); box-shadow: 0 0 0 4px rgba(140,158,255,0.14), 0 0 24px -6px rgba(140,158,255,0.5); }
  .search-wrap input::placeholder { color: var(--text-faint); }
  .hero-stats { display: flex; justify-content: center; gap: 26px; font-family: 'Fira Code', monospace; font-size: 12.5px; color: var(--text-faint); margin-bottom: 6px; }
  .hero-stats b { color: var(--text); font-weight: 600; }

  .controls { padding: 26px 0 8px; }
  .chips { display: flex; gap: 9px; flex-wrap: wrap; justify-content: center; margin-bottom: 6px; }
  .chip {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13px; font-weight: 500;
    padding: 8px 15px; border-radius: 20px; border: 1px solid var(--border);
    background: var(--card); color: var(--text-soft); cursor: pointer;
    display: inline-flex; align-items: center; gap: 7px; transition: all 0.15s ease;
  }
  .chip .dot { width: 8px; height: 8px; border-radius: 50%; }
  .chip .n { font-family: 'Fira Code', monospace; font-size: 10.5px; color: var(--text-faint); }
  .chip:hover { border-color: rgba(255,255,255,0.22); color: var(--text); }
  .chip.active { color: var(--text); font-weight: 600; }

  .sort-row { display: flex; justify-content: center; align-items: center; gap: 16px; margin: 14px 0 8px; font-family: 'Fira Code', monospace; font-size: 12px; color: var(--text-faint); }
  select#sort {
    font-family: 'Fira Code', monospace; font-size: 12px; background: var(--card); color: var(--text-soft);
    border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px; cursor: pointer;
  }

  main { padding: 24px 0 90px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }

  .card {
    background: var(--card);
    border-radius: 16px;
    border: 1px solid rgba(var(--glow-rgb), 0.28);
    box-shadow: 0 0 0 1px rgba(var(--glow-rgb), 0.06), 0 0 26px -10px rgba(var(--glow-rgb), 0.55), 0 10px 24px -12px rgba(0,0,0,0.5);
    padding: 18px;
    display: flex; flex-direction: column;
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
  }
  .card:hover {
    transform: translateY(-3px);
    background: var(--card-hover);
    box-shadow: 0 0 0 1.5px rgba(var(--glow-rgb), 0.55), 0 0 38px -8px rgba(var(--glow-rgb), 0.75), 0 14px 30px -12px rgba(0,0,0,0.6);
  }
  .card-top { display: flex; align-items: flex-start; gap: 11px; margin-bottom: 12px; }
  .favicon {
    width: 34px; height: 34px; border-radius: 9px; background: var(--bg-2);
    border: 1px solid var(--border); display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; overflow: hidden; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 14px; color: var(--text-faint);
  }
  .favicon img { width: 19px; height: 19px; }
  .card-head { flex: 1; min-width: 0; }
  .card h3 { font-family: 'Sora', sans-serif; font-size: 15.5px; font-weight: 700; margin: 0 0 4px; line-height: 1.3; }
  .cat-tag { display: flex; align-items: center; gap: 6px; font-family: 'Fira Code', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-faint); }
  .cat-tag .dot { width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 6px 0 rgba(var(--glow-rgb), 0.9); }
  .verified-badge { display: inline-flex; align-items: center; gap: 3px; font-family: 'Fira Code', monospace; font-size: 9px; font-weight: 600; color: var(--verified); border: 1px solid rgba(var(--verified-rgb),0.4); border-radius: 5px; padding: 1px 5px; margin-top: 5px; }
  .warn-badge { display: inline-flex; align-items: center; gap: 3px; font-family: 'Fira Code', monospace; font-size: 9px; font-weight: 600; color: #FFB454; border: 1px solid rgba(255,180,84,0.4); border-radius: 5px; padding: 1px 5px; margin-top: 5px; }

  .card .benefit {
    font-size: 13.5px; color: var(--text-soft); line-height: 1.55; margin: 0 0 14px; flex: 1;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  }
  .card-foot { display: flex; align-items: center; justify-content: space-between; padding-top: 13px; border-top: 1px solid var(--border); }
  .value-chip { font-family: 'Fira Code', monospace; font-size: 11px; font-weight: 600; background: rgba(var(--glow-rgb),0.14); color: #fff; padding: 4px 9px; border-radius: 6px; }
  .value-chip.empty { visibility: hidden; }
  a.claim { font-size: 13px; font-weight: 600; text-decoration: none; color: var(--text); display: inline-flex; align-items: center; gap: 4px; }
  a.claim:hover { text-decoration: underline; }

  .empty-state { grid-column: 1 / -1; text-align: center; padding: 70px 20px; color: var(--text-soft); font-family: 'Fira Code', monospace; }

  footer { border-top: 1px solid var(--border); padding: 46px 0 60px; }
  .foot-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 40px; margin-bottom: 30px; }
  .foot-title { font-family: 'Fira Code', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-faint); margin-bottom: 12px; display: block; }
  footer p { font-size: 13.5px; color: var(--text-soft); line-height: 1.65; margin: 0; }
  footer ul { list-style: none; padding: 0; margin: 0; }
  footer li { font-size: 13.5px; margin-bottom: 8px; }
  footer a.src { color: var(--text-soft); text-decoration: none; }
  footer a.src:hover { color: #8C9EFF; text-decoration: underline; }
  .foot-bottom { border-top: 1px solid var(--border); padding-top: 20px; font-size: 12.5px; color: var(--text-faint); }
  @media (max-width: 760px) { .foot-grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>

<nav class="navbar">
  <div class="wrap">
    <div class="brand"><span class="mark">S</span>Student Stash</div>
    <div class="nav-badge" id="nav-count">Loading…</div>
  </div>
</nav>
<div class="wrap" id="updated-row" style="display:none; padding-top:8px;">
  <span style="font-family:'Fira Code',monospace; font-size:11px; color:var(--text-faint);" id="updated-text"></span>
</div>

<header class="hero">
  <div class="wrap">
    <p class="eyebrow">399+ Student Offers · One Page</p>
    <h1>Every discount your <span class="grad">.edu status</span> already earned you.</h1>
    <p class="sub">A searchable index of software credits, cloud plans, learning platforms, and everyday discounts — compiled from open, community-maintained sources.</p>
    <div class="search-wrap">
      <input id="search" type="text" placeholder="Search by tool, brand, or category...">
    </div>
    <div class="hero-stats">
      <span><b id="count-showing">…</b> of <b id="count-total">…</b> shown</span>
      <span>&middot;</span>
      <span><b id="count-cats">…</b> categories</span>
      <span>&middot;</span>
      <span><b id="count-verified">…</b> GitHub Ed. verified</span>
    </div>
  </div>
</header>

<div class="controls">
  <div class="wrap">
    <div class="chips" id="chips"></div>
    <div class="sort-row">
      Sort:
      <select id="sort">
        <option value="name">Name (A–Z)</option>
        <option value="category">Category</option>
      </select>
    </div>
  </div>
</div>

<main>
  <div class="wrap">
    <div class="grid" id="grid"></div>
  </div>
</main>

<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <span class="foot-title">About this index</span>
        <p>Student Stash indexes free tools, cloud credits, software licenses, and everyday discounts available to students. Every card links directly to the provider — verify eligibility and current terms there, since offers change often. Cards marked <b>GitHub Ed. Partner</b> were cross-checked against GitHub Education's official current-partner list.</p>
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
    <div class="foot-bottom">Compiled from open-source, MIT-licensed community lists. Not affiliated with any provider listed. Prototype build.</div>
  </div>
</footer>

<script>
let OFFERS = [];
const CAT_COLORS = __COLORS_JSON__;
let CATEGORIES = [];
let TOTAL = 0;
let activeCat = 'All';
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

    document.getElementById('nav-count').textContent = TOTAL + ' offers';
    document.getElementById('count-total').textContent = TOTAL;
    document.getElementById('count-cats').textContent = CATEGORIES.length;
    document.getElementById('count-verified').textContent = OFFERS.filter(o => o.pack_verified).length;
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

    renderChips();
    renderGrid();
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

function catCounts() {
  const counts = {};
  CATEGORIES.forEach(c => counts[c] = 0);
  OFFERS.forEach(o => counts[o.category_clean] = (counts[o.category_clean]||0) + 1);
  return counts;
}
const COUNTS = catCounts();

function renderChips() {
  const chipsEl = document.getElementById('chips');
  const all = [{name:'All', count: TOTAL, color:'#8C9EFF'}, ...CATEGORIES.map(c => ({name:c, count: COUNTS[c], color: CAT_COLORS[c]}))];
  chipsEl.innerHTML = all.map(c => {
    const rgb = hexToRgb(c.color);
    const activeStyle = c.name===activeCat ? `border-color:rgba(${rgb},0.6); box-shadow:0 0 16px -4px rgba(${rgb},0.6); background:rgba(${rgb},0.12);` : '';
    return `<button class="chip ${c.name===activeCat?'active':''}" style="${activeStyle}" data-cat="${c.name}"><span class="dot" style="background:${c.color}"></span>${c.name}<span class="n">${c.count}</span></button>`;
  }).join('');
  chipsEl.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => { activeCat = btn.dataset.cat; renderChips(); renderGrid(); });
  });
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
function faviconDomain(url) { try { return new URL(url).hostname; } catch(e) { return null; } }
function escapeHtml(str) { const div = document.createElement('div'); div.textContent = str; return div.innerHTML; }

function renderGrid() {
  const q = query.trim().toLowerCase();
  let filtered = OFFERS.filter(o => {
    const matchesCat = activeCat === 'All' || o.category_clean === activeCat;
    const hay = (o.name + ' ' + o.benefit + ' ' + o.category_clean + ' ' + o.category).toLowerCase();
    return matchesCat && (!q || hay.includes(q));
  });

  filtered.sort((a,b) => {
    if (sortMode === 'category') {
      const c = a.category_clean.localeCompare(b.category_clean);
      return c !== 0 ? c : a.name.localeCompare(b.name);
    }
    return a.name.localeCompare(b.name);
  });

  document.getElementById('count-showing').textContent = filtered.length;

  const grid = document.getElementById('grid');
  if (filtered.length === 0) {
    grid.innerHTML = `<div class="empty-state">No matches — try a broader search or clear the category filter.</div>`;
    return;
  }

  grid.innerHTML = filtered.map(o => {
    const color = CAT_COLORS[o.category_clean] || '#C8CCDB';
    const rgb = hexToRgb(color);
    const domain = faviconDomain(o.url);
    const value = extractValue(o.benefit);
    const initial = o.name.trim().charAt(0).toUpperCase();
    const candidates = domain ? faviconCandidates(domain) : [];
    const iconHtml = candidates.length
      ? `<img src="${candidates[0]}" data-idx="0" data-domain="${domain}" data-fallback="${initial}" onerror="handleImgError(this)" alt="">`
      : initial;
    return `
      <div class="card" style="--glow-rgb: ${rgb};">
        <div class="card-top">
          <div class="favicon">${iconHtml}</div>
          <div class="card-head">
            <h3>${escapeHtml(o.name)}</h3>
            <span class="cat-tag"><span class="dot" style="background:${color}"></span>${o.category_clean}</span>
            ${o.pack_verified ? '<div class="verified-badge">GITHUB ED. PARTNER</div>' : ''}
            ${o.link_health && ['dead','unreachable','ssl_error','timeout'].includes(o.link_health) ? '<div class="warn-badge">LINK MAY BE DOWN</div>' : ''}
            ${o.content_flag === 'possibly_expired' ? '<div class="warn-badge">OFFER MAY HAVE ENDED</div>' : ''}
          </div>
        </div>
        <p class="benefit">${escapeHtml(o.benefit)}</p>
        <div class="card-foot">
          <span class="value-chip ${value ? '' : 'empty'}">${value || '—'}</span>
          <a class="claim" href="${o.url}" target="_blank" rel="noopener">Get it &rarr;</a>
        </div>
      </div>
    `;
  }).join('');
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
