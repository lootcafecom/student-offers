"""
Student Stash — Shared page-generation helpers.

Used by both generate_category_pages.py and generate_offer_pages.py so the
color palette, template, and utility functions stay identical across every
generated page rather than drifting between two copies.
"""

import re

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
    return s or 'item'


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
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&#39;'))


def favicon_domain(url):
    m = re.match(r'https?://([^/]+)', url)
    return m.group(1) if m else None


def favicon_html(url, name):
    domain = favicon_domain(url)
    initial = name.strip()[0].upper() if name.strip() else '?'
    if not domain:
        return initial
    src = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
    return (f'<img src="{src}" data-idx="0" data-domain="{domain}" '
            f'data-fallback="{initial}" onerror="handleImgError(this)" alt="">')


def warn_badges_html(o):
    html = ''
    if o.get('link_health') in ('dead', 'unreachable', 'ssl_error', 'timeout'):
        html += '<span class="warn-badge">LINK MAY BE DOWN</span>'
    if o.get('content_flag') == 'possibly_expired':
        html += '<span class="warn-badge">OFFER MAY HAVE ENDED</span>'
    return html


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
        <p>Student Stash indexes free tools, cloud credits, software licenses, and everyday discounts available to students. Every entry links directly to the provider — verify eligibility and current terms there, since offers change often.</p>
      </div>
      <div>
        <span class="foot-title">Data sources</span>
        <ul>
          <li><a class="src" href="https://github.com/ShreyamMaity/student-offers" target="_blank" rel="noopener">ShreyamMaity/student-offers ↗</a></li>
          <li><a class="src" href="https://github.com/AchoArnold/discount-for-student-dev" target="_blank" rel="noopener">AchoArnold/discount-for-student-dev ↗</a></li>
          <li><a class="src" href="https://github.com/OpenGenus/Best-student-discount-services" target="_blank" rel="noopener">OpenGenus/Best-student-discount-services ↗</a></li>
          <li><a class="src" href="https://github.com/couponswift/awesome-student-software-deals" target="_blank" rel="noopener">couponswift/awesome-student-software-deals ↗</a></li>
          <li><a class="src" href="https://github.com/jhaxce/student-perks" target="_blank" rel="noopener">jhaxce/student-perks ↗</a></li>
          <li><a class="src" href="https://github.com/kamath/student-free-stuff" target="_blank" rel="noopener">kamath/student-free-stuff ↗</a></li>
          <li><a class="src" href="https://github.com/Aashish-po/edu-email-benefits" target="_blank" rel="noopener">Aashish-po/edu-email-benefits ↗</a></li>
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
