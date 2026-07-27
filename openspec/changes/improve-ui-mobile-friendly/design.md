## Context

ScholarshipFinder is a Django app served entirely by server-rendered templates styled by a single static stylesheet (`scholarships/static/scholarships/style.css`, ~840 lines) plus per-template inline `<script>` snippets. There is no front-end framework and no build step.

Current state relevant to this change:
- `base.html` renders a single `<ul class="nav-links">` that uses `flex: 1 1 auto` per item so links stretch across the viewport. On narrow screens this produces tiny, cramped tap targets and wraps awkwardly.
- The design relies on near-monochrome CSS variables (`--color-bg: #fff`, `--color-text: #1a1a1a`, one teal `--color-info` accent). There is no visual identity, hierarchy, or whitespace rhythm.
- The scholarship list (`scholarship_list.html`) is a wide 9-column table wrapped in `.table-wrapper { overflow-x: auto }`. On phones this forces horizontal scrolling and hides columns — the core "browse" task is poor on mobile.
- Forms, detail, profile, and admin pages are functional but lack consistent spacing, tap-target sizing, and mobile input conventions (e.g. `font-size: 16px` to avoid iOS zoom).
- The only responsive rule is a single `@media (min-width: 768px)` block; below that everything collapses to defaults.

Constraints:
- Keep Django structure intact: no changes to `models.py`, `views.py`, `urls.py`, `forms.py`, or templatetags.
- Keep template block names (`title`, `content`, `extra_js`) and all context variables identical so views are untouched.
- No new Python/runtime dependencies, no JS framework, no CSS framework that would force restructuring.

## Goals / Non-Goals

**Goals:**
- Establish a small, tokenized design system (color, type scale, spacing, radius, shadow) that the existing stylesheet consumes.
- Make every page work comfortably from ~320px upward (mobile-first), with a collapsible header navigation.
- Give the scholarship list a true mobile layout (stacked cards) while keeping the table on larger screens.
- Standardize components (buttons, badges, cards, alerts, tables, forms) for a consistent, modern look.
- Maintain or improve accessibility: WCAG AA contrast, visible focus, `prefers-reduced-motion`, and existing keyboard/ARIA patterns (skip link, `aria-current`, filter `aria-expanded`).

**Non-Goals:**
- No redesign of information architecture, URL routes, or page set.
- No dark mode as a product feature (tokens may be structured to allow it later, but shipping it is out of scope).
- No back-end behavior changes, no new model fields, no API work.
- No replacement of the table with a JS data grid, no infinite scroll, no client-side filtering.
- No addition of Tailwind/Bootstrap or any build pipeline.

## Decisions

**1. Evolve the existing CSS file in place rather than splitting it.**
Rationale: The skill guidance is to avoid changing underlying structure. A single stylesheet keeps the `{% static %}` wiring and template `block` contract identical, and avoids a migration. We *reorganize* it (design tokens at top, layout, components, utilities, media queries) but keep it as one file.
Alternatives considered: splitting into `base.css` / `components.css` (cleaner but changes `base.html` asset wiring and adds coupling); adopting a framework (rejected — forces restructuring and adds a build step).

**2. Add new CSS custom properties; keep existing variable names as aliases.**
Rationale: Existing rules reference `--color-text`, `--color-border`, `--spacing-unit`, `--max-width`, etc. We add a richer token layer (`--brand`, `--brand-600`, `--surface`, `--surface-muted`, `--radius`, `--shadow-sm`, type scale `--text-*`, `--space-*`) and point the legacy names at them. This upgrades the look without rewriting every selector.
Alternatives: rename all tokens (rejected — high churn, risk).

**3. Mobile-first responsive strategy with breakpoints at 480/768/1024px.**
Rationale: Base styles target phone widths; `min-width` media queries progressively enhance to tablet/desktop. This fixes the worst case (mobile) directly and matches the user's stated priority. The existing single `@media (min-width: 768px)` block is retained and extended.

**4. Collapsible header nav via a CSS-driven toggle + tiny vanilla-JS handler.**
Rationale: A true hamburger needs JS to flip an `aria-expanded`/`hidden` state accessibly. We add a `<button class="nav-toggle">` to `base.html` and a ~10-line script in the existing `extra_js`-adjacent area (or inline). The menu is a `<ul>` shown/hidden via a class + `hidden` attribute; keyboard and screen-reader users get correct semantics. No framework, no external dependency.
Alternatives: CSS-only "checkbox hack" (rejected — poor a11y semantics and keyboard support); always-visible wrapping nav (rejected — cramped on phones).

**5. Scholarship list: keep `.scholarship-table` for ≥768px; render stacked cards on <768px.**
Rationale: Tables are the right tool for dense comparison on desktop but fail on phones. To avoid duplicating markup and to keep the view context untouched, we mark each `<td>` with `data-label` (the column name) and use a CSS pattern that turns each row into a stacked card on narrow widths (cells become `display:block` with a generated label via `::before`). This keeps a single source of markup in the template.
Alternatives: server-side separate "mobile" template (rejected — duplicates logic); convert the table to cards entirely (rejected — loses desktop density).

**6. Tap-target and input sizing conventions.**
- All interactive elements ≥44×44px hit area on mobile.
- Form inputs use `font-size: 1rem` (16px) to prevent iOS auto-zoom, `width: 100%`, and comfortable padding.
- Buttons get larger vertical padding on mobile.

**7. Accessibility baseline.**
- Maintain contrast ratio ≥4.5:1 for body text and ≥3:1 for large text/UI boundaries.
- Keep `:focus-visible` outlines (already present) and ensure they remain visible against new backgrounds.
- Honor `@media (prefers-reduced-motion: reduce)` to disable the existing `.text-clamp` height transition and any hover transforms.
- Keep and reuse existing skip link, `aria-current`, `aria-expanded`, and `<details>` filter patterns.

## Risks / Trade-offs

- **[Visual regression on pages not actively reviewed]** → Mitigation: The work covers all 18 templates, but we sequence it so shared `base.html`/tokens land first; every page automatically inherits the token upgrade. Verify each route in the tasks list.
- **[`data-label` card layout duplicates column names in markup]** → Mitigation: acceptable trade-off for zero duplication of rows; labels live only in the list template's `<th>`/`data-label` and are easy to keep in sync. Document in tasks.
- **[Cache-busting of `style.css`]** → Browsers may serve stale CSS after deploy. Mitigation: note in tasks/impact; optionally append a `?v=` query string to the `{% static %}` include in `base.html` (one-line, non-breaking).
- **[Tiny inline JS for nav toggle]** → Adds a small script to `base.html`. Mitigation: keep it dependency-free, progressive-enhancement only (page still fully usable if JS fails — menu degrades to a visible list via a `<noscript>`/default-CSS fallback).
- **[Token layer adds CSS size]** → Negligible (~a few KB). Trade-off accepted for maintainability.
