## 1. Design tokens foundation

- [x] 1.1 In `scholarships/static/scholarships/style.css`, expand the `:root` block with a token layer: brand colors (`--brand`, `--brand-600`, `--accent`), surface colors (`--surface`, `--surface-muted`, `--border`, `--text`, `--text-muted`), type scale (`--text-xs`…`--text-2xl`), spacing scale (`--space-1`…`--space-8`), `--radius`, `--radius-sm`, `--shadow-sm`
- [x] 1.2 Alias the legacy variables (`--color-bg`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-focus`, `--color-success`, `--color-error`, `--color-warning`, `--color-info`, `--spacing-unit`, `--max-width`) to the new tokens so existing selectors keep resolving
- [x] 1.3 Reorganize the stylesheet into clearly commented sections: Tokens → Base → Layout → Components → Page-specific → Utilities → Media queries (content unchanged at this step, only ordering/headers)

## 2. Base layout & typography

- [x] 2.1 Update `body`, headings (`h1`/`h2`/`h3`), `.container`, links, and `a:hover` to consume the type scale and color tokens; ensure body text contrast ≥ 4.5:1
- [x] 2.2 Restyle `.site-header` and `.site-footer` with the new tokens (subtle surface, border, brand accent)
- [x] 2.3 Confirm the `.skip-link` still works and its focus state has sufficient contrast against the new header

## 3. Collapsible navigation

- [x] 3.1 In `scholarships/templates/scholarships/base.html`, wrap `.nav-links` in a container and add a `<button class="nav-toggle" aria-expanded="false" aria-controls="primary-nav">Menu</button>` shown only on narrow viewports
- [x] 3.2 Add `id="primary-nav"` to the nav list and a default-visible fallback so links are reachable when JavaScript is disabled
- [x] 3.3 Add a small dependency-free script (in `base.html`, near the existing `extra_js` block) that toggles a class and the `hidden` attribute on the nav and syncs `aria-expanded` and the button label
- [x] 3.4 Add `.nav-toggle` and collapsed-nav styles: hide toggle ≥768px, hide collapsed links <768px, stack links vertically when expanded, ensure ≥44px tap targets
- [x] 3.5 Verify keyboard access (Tab to toggle, Enter to expand, Tab into links) and that `aria-current="page"` styling still applies

## 4. Home page hero

- [x] 4.1 In `scholarships/templates/scholarships/home.html`, restyle the heading/intro into a hero section using existing context (no new variables)
- [x] 4.2 Convert the "Quick actions" `<ul>` into styled call-to-action buttons (`.button.primary-action` and a secondary button), stacking on mobile
- [x] 4.3 Add `.hero` and quick-action styles to the stylesheet

## 5. Scholarship list — responsive table/cards

- [x] 5.1 In `scholarships/templates/scholarships/scholarship_list.html`, add `data-label="…"` to each `<td>` matching its column header (Type, Foundation, Scholarship Name, Qualifier, Schools, Fields, Grants, Award, App Period)
- [x] 5.2 Add a CSS pattern that, below 768px, turns `.scholarship-table` rows into stacked cards: `display:block` for `tr`/`td`, a `::before` on each cell showing its `data-label`, and a card border/padding
- [x] 5.3 Ensure the existing `.clamp-toggle` buttons and `.section-badge` render correctly inside the stacked card layout
- [x] 5.4 Keep the table layout (with `.table-wrapper`) for ≥768px and verify no horizontal scroll is needed on mobile

## 6. Forms & inputs (mobile-friendly)

- [x] 6.1 Set `font-size: 1rem` (≥16px), `width: 100%`, and comfortable padding on all `form input`, `select`, `textarea` so iOS does not auto-zoom
- [x] 6.2 Increase touch target padding for buttons on mobile (≥44px hit area) in `button`/`.button`
- [x] 6.3 Review `login.html`, `register.html`, `password_change.html`, `request_form.html`, `user_form.html` for consistent `.form-group`/label spacing and full-width inputs on mobile

## 7. Shared components

- [x] 7.1 Buttons: unify `.button`, `.button.small`, `.button.primary-action`, `.button.approve`, `.button.reject` to token-driven padding, radius, and hover/focus states
- [x] 7.2 Badges: restyle `.section-badge` and `.status-badge` (`.status-pending/approved/rejected`) for consistent radius, padding, and AA contrast
- [x] 7.3 Cards/alerts: standardize `.stat-card`, `.request-item`, `.scholarship-preview`, `.user-info-summary`, `.review-actions`, `.request-info`, `.alert-*` to a shared radius/shadow/border treatment
- [x] 7.4 Tables: align `.scholarship-table` and `.admin-table` header/cell styling, hover, and borders

## 8. Detail, profile, admin & request pages

- [x] 8.1 `scholarship_detail.html`: refresh `.scholarship-detail-header`, `.detail-section`, `.detail-list`, `.detail-actions`; verify `.detail-list` responsive grid
- [x] 8.2 `profile.html`: ensure `.request-list`/`.request-item`/`.request-header`/`.admin-notes`/`.profile-actions` stack and remain readable on mobile
- [x] 8.3 `admin_dashboard.html`: verify `.admin-stats`/`.stat-card`/`.action-links`/`.admin-table` on mobile widths
- [x] 8.4 `admin_requests.html` and `admin_request_detail.html`: review `.review-actions`/`.action-buttons`/`.request-review-header` responsiveness
- [x] 8.5 `request_success.html`, `reload_scholarships.html`: check `.import-details`/`.import-warnings`/`.command-line`/`.back-link` on mobile
- [x] 8.6 Ensure the filter panel (`#filter-panel`, `.filter-grid`, `.checkbox-group`, `.filter-actions`) is fully usable at 360px

## 9. Accessibility & motion

- [x] 9.1 Audit all text/background pairs for ≥4.5:1 (body) and ≥3:1 (large text/UI boundaries); adjust tokens as needed
- [x] 9.2 Confirm `:focus-visible` outlines are visible against every new component background
- [x] 9.3 Add `@media (prefers-reduced-motion: reduce)` to disable the `.text-clamp` transition and any hover transforms
- [x] 9.4 Verify the filter toggle's existing `aria-expanded` behavior and the nav toggle's `aria-expanded`/`aria-controls` report correctly

## 10. Verification

- [x] 10.1 Manually exercise every route at 360px, 480px, 768px, and 1024px widths (home, list, detail, login, register, profile, request form/success, admin dashboard/requests/detail, reload, password change) and confirm no horizontal scroll and correct layout
- [x] 10.2 Run keyboard-only navigation across all pages and confirm focus order, focus visibility, and menu/filter toggles work
- [x] 10.3 Run `ruff check . && black --check . && pytest` and confirm no regressions (Python files are unchanged)
- [x] 10.4 (Optional) Add a cache-busting `?v=` query string to the `{% static 'scholarships/style.css' %}` link in `base.html` and note it in the deploy notes
