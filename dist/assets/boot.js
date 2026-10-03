// Keep the page usable even if a later script or image fails to load.
(() => {
  const root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('page-loading');
  const finish = () => root.classList.remove('page-loading');
  const failSafe = window.setTimeout(finish, 1800);
  document.addEventListener('DOMContentLoaded', () => {
    const firstImage = document.querySelector('main img[fetchpriority="high"]');
    if (!firstImage || firstImage.complete) finish();
    else {
      firstImage.addEventListener('load', finish, { once: true });
      firstImage.addEventListener('error', finish, { once: true });
    }
  }, { once: true });
  window.addEventListener('load', () => {
    window.clearTimeout(failSafe);
    finish();
  }, { once: true });
  window.addEventListener('pageshow', finish);
})();
