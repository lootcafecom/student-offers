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
  if (idx < candidates.length) {
    img.dataset.idx = idx;
    img.src = candidates[idx];
  } else {
    img.style.display = 'none';
    img.parentElement.textContent = img.dataset.fallback;
  }
}
window.handleImgError = handleImgError;
