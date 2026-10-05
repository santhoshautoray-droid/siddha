document.documentElement.classList.remove('no-js');

const siteMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
const siteMotionPaused = () => siteMotionQuery.matches || document.documentElement.classList.contains('motion-paused');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.nav-links');

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
    if (window.innerWidth > 1180) setMenuOpen(false);
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
if (statsSection && 'IntersectionObserver' in window) {
  const statCards = [...statsSection.querySelectorAll('.home-stat')];
  const numberFormat = new Intl.NumberFormat();

  if (!siteMotionPaused()) {
    statCards.forEach((card) => {
      const counter = card.querySelector('[data-count-to]');
      if (counter) counter.textContent = '0';
    });
  }

  const countUp = (counter) => {
    if (counter.dataset.counted === 'true') return;
    counter.dataset.counted = 'true';
    const target = Number(counter.dataset.countTo);
    const duration = 3000;
    const startedAt = performance.now();
    counter.textContent = '0';

    const update = (now) => {
      if (siteMotionPaused()) {
        counter.textContent = numberFormat.format(target);
        return;
      }
      const progress = Math.min((now - startedAt) / duration, 1);
      counter.textContent = numberFormat.format(Math.round(target * progress));
      if (progress < 1) requestAnimationFrame(update);
    };

    requestAnimationFrame(update);
  };

  statCards.forEach((card) => {
    const counter = card.querySelector('[data-count-to]');
    if (!counter) return;

    const statsObserver = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      statsObserver.unobserve(card);
      if (siteMotionPaused()) {
        counter.textContent = numberFormat.format(Number(counter.dataset.countTo));
        counter.dataset.counted = 'true';
      } else {
        countUp(counter);
      }
    }, { threshold: 0.35 });

    statsObserver.observe(card);
  });
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
