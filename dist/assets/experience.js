(() => {
  'use strict';

  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const preferenceKey = 'siddha365-motion-paused';
  let userPaused = false;
  try { userPaused = sessionStorage.getItem(preferenceKey) === 'true'; } catch (_) { /* Preferences are optional. */ }
  const motionPaused = () => userPaused || reducedMotion.matches;
  document.querySelectorAll('[data-treatment-wall]').forEach((wall) => {
    const rows = [...wall.querySelectorAll('[data-treatment-row]')];
    let visible = false;
    let frame = 0;
    const render = () => {
      frame = 0;
      const bounds = wall.getBoundingClientRect();
      const progress = Math.max(0, Math.min(1, (innerHeight - bounds.top) / (innerHeight + bounds.height)));
      const travel = innerWidth <= 600 ? 130 : 280;
      rows.forEach((row, index) => {
        const offset = motionPaused() ? -180 : -180 + (index % 2 ? -1 : 1) * (progress - .5) * travel;
        row.style.transform = `translate3d(${offset.toFixed(2)}px,0,0)`;
      });
    };
    const schedule = () => { if (visible && !frame) frame = requestAnimationFrame(render); };
    new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; if (visible) schedule(); }).observe(wall);
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    document.addEventListener('siddha:motionchange', render);
    reducedMotion.addEventListener('change', render);
  });
  const motionButtons = [...document.querySelectorAll('[data-motion-toggle]')];

  const applyMotionPreference = () => {
    const paused = motionPaused();
    root.classList.toggle('motion-paused', paused);
    root.classList.toggle('motion-reduced', reducedMotion.matches);
    motionButtons.forEach((button) => {
      const label = reducedMotion.matches ? 'Motion reduced' : (paused ? 'Resume motion' : 'Pause motion');
      const labelElement = button.querySelector('[data-motion-label]');
      if (labelElement) labelElement.textContent = label;
      else button.textContent = label;
      button.setAttribute('aria-pressed', String(paused));
      button.setAttribute('aria-label', label);
      button.disabled = reducedMotion.matches;
      button.title = reducedMotion.matches
        ? 'Motion is reduced by your device accessibility settings.'
        : `${label} across the website`;
    });
    document.dispatchEvent(new CustomEvent('siddha:motionchange', { detail: { paused } }));
  };

  motionButtons.forEach((button) => {
    button.addEventListener('click', () => {
      userPaused = !userPaused;
      try { sessionStorage.setItem(preferenceKey, String(userPaused)); } catch (_) { /* Keep the preference for this page. */ }
      applyMotionPreference();
    });
  });
  reducedMotion.addEventListener?.('change', applyMotionPreference);
  applyMotionPreference();
  root.classList.add('motion-ready');

  let tabSetCount = 0;
  const enhanceTabs = (container, tabAttribute, panelAttribute) => {
    const tabs = [...container.querySelectorAll(`[${tabAttribute}]`)];
    const panels = [...container.querySelectorAll(`[${panelAttribute}]`)];
    const pairs = tabs.map((tab) => ({
      tab,
      panel: panels.find((panel) => panel.getAttribute(panelAttribute) === tab.getAttribute(tabAttribute))
    }));
    if (!pairs.length || pairs.some(({ panel }) => !panel)) return;
    const tabList = pairs[0].tab.closest('[role="tablist"]');
    if (!tabList) return;
    const idPrefix = `experience-tabs-${++tabSetCount}`;
    let selectedIndex = 0;
    const animationTimers = new WeakMap();

    pairs.forEach(({ tab, panel }, index) => {
      tab.type = 'button';
      tab.id ||= `${idPrefix}-tab-${index}`;
      panel.id ||= `${idPrefix}-panel-${index}`;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', panel.id);
      panel.setAttribute('role', 'tabpanel');
      panel.setAttribute('aria-labelledby', tab.id);
      panel.tabIndex = 0;
    });

    const selectTab = (index, animate = true) => {
      selectedIndex = index;
      pairs.forEach(({ tab, panel }, position) => {
        const selected = position === index;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
        tab.classList.toggle('is-active', selected);
        panel.hidden = !selected;
        panel.classList.remove('is-entering');
        window.clearTimeout(animationTimers.get(panel));
        if (selected && animate && !motionPaused()) {
          panel.classList.add('is-entering');
          animationTimers.set(panel, window.setTimeout(() => panel.classList.remove('is-entering'), 450));
        }
      });
      if (container.hasAttribute('data-visit-journey')) {
        container.dataset.activeStep = pairs[index].tab.getAttribute(tabAttribute);
      }
    };

    pairs.forEach(({ tab }, index) => {
      tab.addEventListener('click', () => {
        if (selectedIndex !== index) selectTab(index);
      });
      tab.addEventListener('keydown', (event) => {
        let nextIndex;
        if (event.key === 'Home') nextIndex = 0;
        else if (event.key === 'End') nextIndex = pairs.length - 1;
        else if (event.key === 'ArrowRight') nextIndex = (index + 1) % pairs.length;
        else if (event.key === 'ArrowLeft') nextIndex = (index - 1 + pairs.length) % pairs.length;
        else return;
        event.preventDefault();
        selectTab(nextIndex);
        pairs[nextIndex].tab.focus();
      });
    });
    selectTab(0, false);
    container.classList.add('is-enhanced');
  };

  document.querySelectorAll('[data-care-explorer]').forEach((container) => {
    enhanceTabs(container, 'data-care-tab', 'data-care-panel');
  });
  document.querySelectorAll('[data-visit-journey]').forEach((container) => {
    enhanceTabs(container, 'data-visit-step', 'data-visit-panel');
  });

  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  document.querySelectorAll('[data-hero-glow]').forEach((glow) => {
    const hero = glow.closest('.home-gallery-section');
    if (!hero) return;
    let frame = 0;
    let offsetX = 0;
    let offsetY = 0;
    const reset = () => {
      cancelAnimationFrame(frame);
      frame = 0;
      offsetX = 0;
      offsetY = 0;
      glow.style.transform = 'translate3d(0, 0, 0)';
    };
    hero.addEventListener('pointermove', (event) => {
      if (motionPaused() || !finePointer.matches || document.hidden || event.pointerType === 'touch') return;
      const bounds = hero.getBoundingClientRect();
      if (!bounds.width || !bounds.height) return;
      offsetX = Math.max(-20, Math.min(20, ((event.clientX - bounds.left) / bounds.width - 0.5) * 40));
      offsetY = Math.max(-20, Math.min(20, ((event.clientY - bounds.top) / bounds.height - 0.5) * 40));
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        glow.style.transform = `translate3d(${offsetX.toFixed(2)}px, ${offsetY.toFixed(2)}px, 0)`;
      });
    }, { passive: true });
    hero.addEventListener('pointerleave', reset);
    document.addEventListener('siddha:motionchange', reset);
    document.addEventListener('visibilitychange', reset);
    finePointer.addEventListener?.('change', reset);
  });
})();
