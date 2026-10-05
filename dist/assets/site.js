document.documentElement.classList.remove('no-js');

const siteMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
const siteMotionPaused = () => siteMotionQuery.matches || document.documentElement.classList.contains('motion-paused');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.nav-links');
const siteHeader = document.querySelector('.site-header');

// Keep the practitioner introduction close to the hero, before the broader
// traditional-care explanation on the homepage.
const founderSection = document.querySelector('.home-founder-section');
const introSection = document.querySelector('.home-intro');
if (founderSection && introSection) introSection.before(founderSection);

const careLabelUpdates = { women: 'Women’s Health Care', skin: 'Skin & Hair', movement: 'Joints & Cupping Therapy', family: 'Family & Child Care' };
Object.entries(careLabelUpdates).forEach(([key, label]) => {
  const tab = document.querySelector(`[data-care-tab="${key}"]`);
  if (tab?.firstChild?.nodeType === Node.TEXT_NODE) tab.firstChild.nodeValue = label;
  const eyebrow = document.querySelector(`#care-panel-${key} .care-panel-intro .eyebrow`);
  if (eyebrow?.firstChild?.nodeType === Node.TEXT_NODE) eyebrow.firstChild.nodeValue = label;
});

// Keep the navigation out of the way while reading down the page, then restore it
// as soon as the visitor scrolls back up. The menu always stays visible when open.
if (siteHeader) {
  let previousScrollY = Math.max(window.scrollY, 0);
  let scrollFrame = 0;
  const updateHeaderVisibility = () => {
    scrollFrame = 0;
    const currentScrollY = Math.max(window.scrollY, 0);
    const menuIsOpen = menuButton?.getAttribute('aria-expanded') === 'true';
    if (currentScrollY <= 24 || currentScrollY < previousScrollY || menuIsOpen) {
      siteHeader.classList.remove('header-scroll-hidden');
    } else if (currentScrollY > previousScrollY) {
      siteHeader.classList.add('header-scroll-hidden');
    }
    previousScrollY = currentScrollY;
  };
  window.addEventListener('scroll', () => {
    if (!scrollFrame) scrollFrame = window.requestAnimationFrame(updateHeaderVisibility);
  }, { passive: true });
}

if (menuButton && navigation) {
  const setMenuOpen = (isOpen) => {
    navigation.classList.toggle('is-open', isOpen);
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  };

  menuButton.addEventListener('click', () => {
    setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true');
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenuOpen(false);
  });

  document.addEventListener('pointerdown', (event) => {
    if (!event.target.closest('.site-header') && menuButton.getAttribute('aria-expanded') === 'true') setMenuOpen(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenuOpen(false);
      menuButton.focus();
    }
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 1040) setMenuOpen(false);
  });
}

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !siteMotionPaused()) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12 });
  revealItems.forEach((item) => { item.classList.add('reveal-pending'); revealObserver.observe(item); });
  const finishReveals = () => {
    if (!siteMotionPaused()) return;
    revealObserver.disconnect();
    revealItems.forEach((item) => item.classList.add('is-visible'));
  };
  document.addEventListener('siddha:motionchange', finishReveals);
  siteMotionQuery.addEventListener?.('change', finishReveals);
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

const statsSection = document.querySelector('.home-stats-band');
if (statsSection) {
  const milestones = [
    { value: 5, label: 'Years of experience', detail: 'Thoughtful, personal Siddha care', icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 3v4m8-4v4M4 10h16m-7 3v4l3 2"/></svg>' },
    { value: 500, label: 'Health concerns supported', detail: 'Individual concerns, carefully heard', icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.3-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.7-7 10-7 10Z"/><path d="M8.5 12h2l1.2-2.2 1.5 4 1.1-1.8h1.4"/></svg>' },
    { value: 700, label: 'Treatments', detail: 'Care plans considered with clarity', icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5h8v4a4 4 0 0 1-8 0V5Zm4 8v6m-3-3h6"/><path d="M5 5h2m10 0h2"/></svg>' },
    { value: 5000, label: 'Clients served', detail: 'People and families across Chennai', icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3"/><path d="M6 20c.6-3.5 2.7-5 6-5s5.4 1.5 6 5M5.5 11.5a2.3 2.3 0 1 1 1.6-4M18.5 11.5a2.3 2.3 0 1 0-1.6-4"/></svg>' },
  ];
  const background = statsSection.querySelector('.home-stats-background');
  const formatNumber = new Intl.NumberFormat('en-IN');
  const displayNumber = (value) => value === 5 ? '05' : formatNumber.format(value);

  statsSection.classList.add('clinic-statistics');
  statsSection.innerHTML = `
    ${background ? background.outerHTML : ''}
    <div class="clinic-statistics__veil" aria-hidden="true"></div>
    <div class="container clinic-statistics__inner">
      <header class="clinic-statistics__header">
        <p class="eyebrow">Siddha365 milestones</p>
      </header>
      <div class="clinic-statistics__grid" aria-label="Siddha365 clinic statistics">
        ${milestones.map((milestone, index) => `<article class="clinic-statistic" style="--stat-index:${index}"><span class="clinic-statistic__icon">${milestone.icon}</span><strong data-stat-count="${milestone.value}" aria-label="${displayNumber(milestone.value)} ${milestone.label}">${displayNumber(milestone.value)}</strong><span class="clinic-statistic__label">${milestone.label}</span><span class="clinic-statistic__detail">${milestone.detail}</span><span class="clinic-statistic__line" aria-hidden="true"></span></article>`).join('')}
      </div>
    </div>`;
  const counters = [...statsSection.querySelectorAll('[data-stat-count]')];
  const finishCounters = () => counters.forEach((counter) => { counter.textContent = displayNumber(Number(counter.dataset.statCount)); });
  const animateCounters = () => {
    if (statsSection.dataset.counted === 'true') return;
    statsSection.dataset.counted = 'true';
    statsSection.classList.add('is-revealed');
    if (siteMotionPaused()) return finishCounters();
    counters.forEach((counter, index) => {
      const target = Number(counter.dataset.statCount);
      const startedAt = performance.now() + (index * 80);
      const duration = 760;
      const update = (now) => {
        if (now < startedAt) return requestAnimationFrame(update);
        const progress = Math.min(1, (now - startedAt) / duration);
        const eased = 1 - ((1 - progress) ** 3);
        const value = Math.round(target * eased);
        counter.textContent = value < 10 ? String(value).padStart(2, '0') : formatNumber.format(value);
        if (progress < 1) requestAnimationFrame(update);
      };
      requestAnimationFrame(update);
    });
  };

  if (siteMotionPaused() || !('IntersectionObserver' in window)) {
    statsSection.classList.add('is-revealed');
    finishCounters();
  } else {
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();
      animateCounters();
    }, { threshold: .3 });
    observer.observe(statsSection);
  }
}

document.querySelectorAll('[data-carousel]').forEach((carousel) => {
  const track = carousel.querySelector('[data-carousel-track]');
  if (!track) return;
  const step = () => {
    if (track.dataset.scrollStep === 'full') {
      const slideWidth = track.firstElementChild?.getBoundingClientRect().width || track.clientWidth;
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return slideWidth + gap;
    }
    return Math.max(track.clientWidth * 0.82, 280);
  };

  carousel.querySelector('[data-carousel-prev]')?.addEventListener('click', () => {
    track.scrollBy({ left: -step(), behavior: siteMotionPaused() ? 'instant' : 'smooth' });
  });
  carousel.querySelector('[data-carousel-next]')?.addEventListener('click', () => {
    track.scrollBy({ left: step(), behavior: siteMotionPaused() ? 'instant' : 'smooth' });
  });

  if (track.dataset.autoplay === 'true') {
    let paused = false;
    let hovered = false;
    let focused = false;
    let timer;
    const pauseButton = carousel.querySelector('[data-carousel-pause]');
    const schedule = () => {
      window.clearInterval(timer);
      timer = window.setInterval(() => {
        if (paused || hovered || focused || siteMotionPaused() || document.hidden || document.querySelector('dialog[open]') || !track.getBoundingClientRect().height || track.getBoundingClientRect().bottom < 0 || track.getBoundingClientRect().top > innerHeight) return;
        const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 12;
        track.scrollTo({ left: atEnd ? 0 : track.scrollLeft + step(), behavior: 'smooth' });
      }, 6200);
    };

    pauseButton?.addEventListener('click', () => {
      paused = !paused;
      pauseButton.setAttribute('aria-pressed', String(paused));
      pauseButton.textContent = paused ? 'Play' : 'Pause';
      schedule();
    });
    track.addEventListener('pointerenter', () => { hovered = true; });
    track.addEventListener('pointerleave', () => { hovered = false; });
    track.addEventListener('focusin', () => { focused = true; });
    track.addEventListener('focusout', (event) => {
      if (!track.contains(event.relatedTarget)) focused = false;
    });
    schedule();
  }
});

document.querySelectorAll('[data-video-rail]').forEach((rail) => {
  const track = rail.querySelector('[data-video-rail-track]');
  if (!track) return;

  const cards = [...track.children];
  if (cards.length < 2) return;

  const clones = cards.map((card) => {
    const clone = card.cloneNode(true);
    clone.classList.add('is-duplicate');
    clone.setAttribute('aria-hidden', 'true');
    clone.querySelectorAll('button').forEach((button) => { button.tabIndex = -1; });
    return clone;
  });
  track.prepend(...clones);

  let activeIndex = cards.length;
  let inView = !('IntersectionObserver' in window);
  let hovered = false;
  let focused = false;
  const stepSize = () => {
    const firstCard = cards[0];
    const gap = parseFloat(getComputedStyle(track).rowGap) || 0;
    return firstCard.getBoundingClientRect().height + gap;
  };

  const observer = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => { inView = entries.some((entry) => entry.isIntersecting); }, { threshold: 0.1 })
    : null;
  observer?.observe(rail);

  const advance = () => {
    if (document.hidden || !inView || hovered || focused || siteMotionPaused() || document.querySelector('dialog[open]')) return;
    activeIndex -= 1;
    track.classList.add('is-moving');
    track.style.transform = `translateY(${-stepSize() * activeIndex}px)`;
  };

  track.addEventListener('transitionend', (event) => {
    if (event.propertyName !== 'transform' || activeIndex > 0) return;
    track.classList.remove('is-moving');
    activeIndex = cards.length;
    track.style.transform = `translateY(${-stepSize() * activeIndex}px)`;
    track.offsetHeight;
  });

  rail.addEventListener('pointerenter', () => { hovered = true; });
  rail.addEventListener('pointerleave', () => { hovered = false; });
  rail.addEventListener('focusin', () => { focused = true; });
  rail.addEventListener('focusout', (event) => {
    if (!rail.contains(event.relatedTarget)) focused = false;
  });
  const syncRailMotion = () => {
    const paused = siteMotionPaused();
    rail.classList.toggle('is-static', paused);
    track.classList.remove('is-moving');
    activeIndex = paused ? 0 : cards.length;
    track.style.transform = paused ? 'translateY(0)' : `translateY(${-stepSize() * activeIndex}px)`;
    track.querySelectorAll('.is-duplicate').forEach((clone) => { clone.hidden = paused; });
  };
  document.addEventListener('siddha:motionchange', syncRailMotion);
  siteMotionQuery.addEventListener?.('change', syncRailMotion);
  syncRailMotion();
  window.setInterval(advance, 4400);
});

const videoDialog = document.querySelector('#video-dialog');
let videoLoadTimer;
let videoEntrance;
let videoTrigger;
document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-youtube-id]');
  if (!button || !videoDialog || videoDialog.open) return;
  const videoId = button.dataset.youtubeId;
  if (!/^[A-Za-z0-9_-]{11}$/.test(videoId || '')) return;
  const player = document.createElement('iframe');
  player.src = `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&autoplay=1`;
  player.title = button.dataset.youtubeTitle || 'Siddha365 video';
  player.referrerPolicy = 'strict-origin-when-cross-origin';
  player.allow = 'autoplay; encrypted-media; picture-in-picture';
  player.allowFullscreen = true;
  const host = videoDialog.querySelector('[data-video-player]');
  if (!host || typeof videoDialog.showModal !== 'function') return;
  videoTrigger = button;
  const sourceBounds = button.getBoundingClientRect();
  window.clearTimeout(videoLoadTimer);
  host.classList.add('is-loading');
  player.addEventListener('load', () => {
    window.clearTimeout(videoLoadTimer);
    host.classList.remove('is-loading');
  }, { once: true });
  host.replaceChildren(player);
  videoLoadTimer = window.setTimeout(() => host.classList.remove('is-loading'), 10000);
  const fallback = document.createElement('a');
  fallback.className = 'text-link video-external-link';
  fallback.href = `https://www.youtube.com/watch?v=${videoId}`;
  fallback.target = '_blank';
  fallback.rel = 'noopener noreferrer';
  fallback.textContent = 'Watch on YouTube';
  videoDialog.querySelector('.video-external-link')?.remove();
  host.after(fallback);
  videoDialog.querySelector('#video-dialog-title').textContent = player.title;
  videoDialog.showModal();
  videoEntrance?.cancel();
  if (!siteMotionPaused() && typeof videoDialog.animate === 'function') {
    const desktop = window.matchMedia('(min-width: 801px) and (pointer: fine)').matches;
    const targetBounds = videoDialog.getBoundingClientRect();
    const offsetX = Math.max(-70, Math.min(70, sourceBounds.left + sourceBounds.width / 2 - targetBounds.left - targetBounds.width / 2));
    const offsetY = Math.max(-50, Math.min(50, sourceBounds.top + sourceBounds.height / 2 - targetBounds.top - targetBounds.height / 2));
    videoEntrance = videoDialog.animate(desktop ? [
      { opacity: 0, transform: `translate(${offsetX}px, ${offsetY}px) scale(.94)` },
      { opacity: 1, transform: 'translate(0, 0) scale(1)' }
    ] : [{ opacity: 0 }, { opacity: 1 }], {
      duration: desktop ? 220 : 160,
      easing: 'cubic-bezier(.2,.8,.2,1)'
    });
  }
});
videoDialog?.addEventListener('close', () => {
  videoEntrance?.cancel();
  videoEntrance = null;
  window.clearTimeout(videoLoadTimer);
  videoDialog.querySelector('[data-video-player]').replaceChildren();
  videoDialog.querySelector('.video-external-link')?.remove();
  if (videoTrigger?.isConnected && !videoTrigger.closest('[aria-hidden="true"]')) {
    videoTrigger.focus({ preventScroll: true });
  }
  videoTrigger = null;
});
const stopVideoEntrance = () => { if (siteMotionPaused()) videoEntrance?.cancel(); };
document.addEventListener('siddha:motionchange', stopVideoEntrance);
siteMotionQuery.addEventListener?.('change', stopVideoEntrance);

document.querySelectorAll('main img').forEach((img) => {
  const frame = img.closest('.home-slide, .home-intro-image, .split-image, .gallery-item, .tradition-art, .nasagra-art, .video-poster, .home-video-poster');
  const finish = () => {
    frame?.classList.remove('media-loading');
    img.classList.remove('media-pending');
    if (img.naturalWidth) img.classList.add('image-arrived');
    else if (frame) {
      frame.classList.add('media-unavailable');
      frame.setAttribute('aria-label', img.alt || 'Image unavailable');
    }
  };
  if (img.complete) return;
  img.addEventListener('load', finish, { once: true });
  img.addEventListener('error', finish, { once: true });
  if (frame) { frame.classList.add('media-loading'); img.classList.add('media-pending'); }
});

const visitDialog = document.querySelector('#visit-dialog');
if (visitDialog) {
  let alreadySeen = false;
  try { alreadySeen = sessionStorage.getItem('siddha365-visit-dialog') === 'seen'; } catch (_) { /* Storage may be unavailable in file previews. */ }
  if (!alreadySeen) {
    window.setTimeout(() => {
      if (!visitDialog.isConnected || document.querySelector('dialog[open]')) return;
      if (typeof visitDialog.showModal === 'function') visitDialog.showModal();
      else visitDialog.setAttribute('open', '');
      try { sessionStorage.setItem('siddha365-visit-dialog', 'seen'); } catch (_) { /* The dialog still works without storage. */ }
    }, 8500);
  }
}

document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog && typeof dialog.close === 'function') dialog.close();
  });
  dialog.querySelectorAll('[data-dialog-close]').forEach((button) => {
    button.addEventListener('click', () => dialog.close());
  });
});
