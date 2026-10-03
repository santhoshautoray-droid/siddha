# Google review integration

The homepage and `/reviews/` fetch the existing clinic review widget from:
`https://siddha365.com/wp-json/wp/v2/pages/7?_fields=content`

There are no hardcoded or generated testimonials. Cards use the widget's full review text, rating, author name, relative date and Google contributor attribution. Long reviews open in a readable dialog. The two rows loop automatically and pause on hover or keyboard focus.

The browser checks the feed every 60 seconds while the review section is near the viewport and the tab is visible. A new Google review appears only after the clinic's existing widget has synchronized it. This is not a direct, instant Google Reviews API connection. Widget availability, its Google synchronization interval and its review selection remain upstream dependencies.

If the feed fails initially, the site displays an unavailable message instead of testimonial placeholders. If a refresh fails after a successful fetch, the actual previously retrieved reviews remain visible with a connection status. Reviews are not saved to local storage.

## Deployment dependency

If the static site replaces the existing WordPress site on `siddha365.com`, preserve/proxy this endpoint or replace it with an authenticated server-side Google Business Profile integration. The static `dist/` alone does not provide this endpoint. Do not put Google API secrets in browser JavaScript. Keep any replacement feed restricted to the clinic's location and update the CSP connect allowlist and the exact endpoint check in `assets/reviews.js` together.

The current client accepts only the expected HTTPS endpoint, caps responses to 1 MB, applies a 10-second timeout, uses text-only rendering, and allows reviewer links only on the Google Maps contributor path. This validates the transport/format and attribution, not independent proof of each review's authenticity. The original Google listing remains the source of truth.
