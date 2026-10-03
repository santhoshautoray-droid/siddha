// Reviews are fetched from the clinic's existing Google review widget.
// There is intentionally no stored or generated testimonial fallback.
document.querySelectorAll('[data-live-reviews-url]').forEach((container) => {
  const rowsHost = container.querySelector('[data-review-rows]');
  const rows = [...container.querySelectorAll('.review-marquee')];
  const placeholder = container.querySelector('[data-review-placeholder]');
  const status = container.querySelector('[data-review-status]');
  let inFlight = false;
  let active = false;
  let lastSuccess = null;
  let signature = '';

  const readJson = async (response) => {
    const limit = 1_000_000;
    if (!response.ok || !/^application\/json\b/i.test(response.headers.get('content-type') || '')) throw new Error('Feed unavailable');
    if (Number(response.headers.get('content-length')) > limit) throw new Error('Feed too large');
    const reader = response.body?.getReader();
    if (!reader) throw new Error('Feed unavailable');
    const chunks = [];
    let length = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      length += value.byteLength;
      if (length > limit) { await reader.cancel(); throw new Error('Feed too large'); }
      chunks.push(value);
    }
    const data = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { data.set(chunk, offset); offset += chunk.byteLength; }
    return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(data));
  };

  const parseReviews = (html) => {
    if (typeof html !== 'string' || html.length > 1_000_000) throw new Error('Invalid review feed');
    const template = document.createElement('template');
    template.innerHTML = html;
    const seen = new Set();
    return [...template.content.querySelectorAll('.grwp_body .swiper-wrapper .swiper-slide')].slice(0, 50).flatMap((slide) => {
      const author = slide.querySelector('.gr-inner-header a');
      const name = author?.textContent.trim();
      const text = slide.querySelector('.gr-inner-body p')?.textContent.trim();
      const date = slide.querySelector('.gr-stars .time')?.textContent.trim() || '';
      const stars = [...slide.querySelectorAll('.gr-stars .stars-wrapper img')].filter((star) => /\/svg-star\.svg$/.test(star.getAttribute('src') || '')).length;
      let profile;
      try { profile = new URL(author?.getAttribute('href')); } catch (_) { return []; }
      // Require the source widget's Google author attribution and a real rating.
      if (profile.origin !== 'https://www.google.com' || !/^\/maps\/contrib\/\d+\/?$/.test(profile.pathname)
        || !name || name.length > 120 || !text || text.length > 12000 || stars < 1 || stars > 5) return [];
      const key = profile.pathname + text;
      if (seen.has(key)) return [];
      seen.add(key);
      return [{ name, text, date: date.slice(0, 60), stars, profile: profile.href }];
    }).slice(0, 24);
  };

  const makeCard = (review, full = false) => {
    const card = document.createElement('article');
    card.className = 'review-card';
    const stars = document.createElement('p');
    stars.className = 'stars';
    stars.setAttribute('aria-label', `${review.stars} out of 5 stars`);
    stars.textContent = '★'.repeat(review.stars);
    const quote = document.createElement('blockquote');
    quote.textContent = review.text;
    const byline = document.createElement('div');
    byline.className = 'review-by';
    const avatar = document.createElement('span');
    avatar.className = 'review-avatar';
    avatar.setAttribute('aria-hidden', 'true');
    avatar.textContent = review.name.slice(0, 1).toUpperCase();
    const attribution = document.createElement('div');
    const author = document.createElement('a');
    author.href = review.profile;
    author.target = '_blank';
    author.rel = 'noopener noreferrer';
    author.textContent = review.name;
    author.setAttribute('aria-label', `${review.name} — Google reviewer profile`);
    const date = document.createElement('span');
    date.className = 'review-date';
    date.textContent = `Google review${review.date ? ` · ${review.date}` : ''}`;
    attribution.append(author, date);
    byline.append(avatar, attribution);
    card.append(stars, quote, byline);
    if (!full) {
      const read = document.createElement('button');
      read.type = 'button';
      read.className = 'review-read';
      read.textContent = 'Read full review';
      read.addEventListener('click', () => {
        const dialog = document.querySelector('#review-dialog');
        dialog.querySelector('#review-dialog-title').textContent = `${review.name}’s review`;
        dialog.querySelector('[data-review-detail]').replaceChildren(makeCard(review, true));
        dialog.showModal();
      });
      card.append(read);
    }
    return card;
  };

  const render = (reviews) => {
    const nextSignature = JSON.stringify(reviews);
    if (signature === nextSignature) return;
    signature = nextSignature;
    rows.forEach((row, index) => {
      const items = reviews.filter((_, itemIndex) => itemIndex % rows.length === index);
      row.hidden = !items.length;
      const group = row.querySelector('[data-review-group]');
      const duplicate = row.querySelector('[data-review-duplicate]');
      group.replaceChildren(...items.map((review) => makeCard(review)));
      // Keep the visible loop copy clickable without repeating keyboard stops.
      duplicate.replaceChildren(...items.map((review) => {
        const card = makeCard(review);
        card.querySelectorAll('a, button').forEach((control) => { control.tabIndex = -1; });
        return card;
      }));
    });
    rowsHost.hidden = false;
    placeholder.hidden = true;
  };

  const refresh = async () => {
    if (inFlight || document.hidden || !active) return;
    inFlight = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 10000);
    try {
      const endpoint = new URL(container.dataset.liveReviewsUrl);
      if (endpoint.href !== 'https://siddha365.com/wp-json/wp/v2/pages/7?_fields=content') throw new Error('Untrusted review endpoint');
      const response = await fetch(endpoint, { headers: { Accept: 'application/json' }, credentials: 'omit', mode: 'cors', redirect: 'error', cache: 'no-store', signal: controller.signal });
      const data = await readJson(response);
      const reviews = parseReviews(data?.content?.rendered);
      if (!reviews.length) throw new Error('No attributed reviews available');
      render(reviews);
      lastSuccess = new Date();
      container.dataset.feedStatus = 'connected';
      status.textContent = `Google review feed · Checked ${lastSuccess.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · Refreshes automatically`;
    } catch (_) {
      container.dataset.feedStatus = lastSuccess ? 'stale' : 'unavailable';
      if (lastSuccess) {
        status.textContent = `Connection interrupted · Showing reviews retrieved at ${lastSuccess.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}. Retrying automatically.`;
      } else {
        placeholder.querySelector('[data-review-placeholder-title]').textContent = 'Reviews are temporarily unavailable';
        placeholder.querySelector('[data-review-placeholder-copy]').textContent = 'We couldn’t connect to the clinic’s Google review feed. Please check again shortly.';
        status.textContent = 'The feed reconnects automatically. No placeholder reviews are displayed.';
      }
    } finally {
      window.clearTimeout(timeout);
      inFlight = false;
    }
  };
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => {
      active = entries.some((entry) => entry.isIntersecting);
      if (active) refresh();
    }, { rootMargin: '350px' }).observe(container);
  } else { active = true; refresh(); }
  window.setInterval(refresh, 60000);
  window.addEventListener('online', refresh);
  document.addEventListener('visibilitychange', refresh);
});
