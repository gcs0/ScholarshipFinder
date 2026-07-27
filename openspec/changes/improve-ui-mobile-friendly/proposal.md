## Why

The site's current UI is a plain, unstyled-feeling plain CSS sheet with no visual identity, a cramped desktop-centric layout, and a navigation/table experience that breaks down badly on phones. As a scholarship discovery tool likely to be browsed by students on mobile devices, the lack of polish and mobile support hurts usability and credibility. This change modernizes the look and feel and makes every page genuinely mobile-friendly while leaving the Django structure (models, views, URLs, template hierarchy) intact.

## What Changes

- Introduce a cohesive design system (color palette, typography scale, spacing tokens, shadows, radii) layered onto the existing CSS custom properties, without ripping out the current stylesheet.
- Add a responsive, accessible site header with a collapsible "hamburger" navigation menu for narrow viewports (replacing the flex-stretched nav that overflows on phones).
- Restyle the home page into a welcoming hero with clear primary calls-to-action.
- Make the scholarship list responsive: keep the existing table on wider screens, and render a stacked "card" layout on mobile so columns never require horizontal scrolling.
- Improve form, detail, profile, and admin pages with consistent spacing, larger tap targets, and full-width inputs on mobile.
- Standardize button, badge, card, alert, and table treatments for visual consistency.
- Improve focus styles, color contrast (target WCAG AA), and reduced-motion support.
- Preserve the existing template blocks, view contexts, and `{% static %}` asset wiring so no Python code needs to change.

## Capabilities

### New Capabilities
- `frontend-ui`: Responsive, mobile-first presentation layer and design system covering layout, navigation, typography, color, and component styling shared across all scholarship pages.

### Modified Capabilities
<!-- None. No spec-level requirement changes to project-scaffold, django-project, or scholarship-models; changes are presentation-only. -->

## Impact

- **Code affected**: `scholarships/static/scholarships/style.css` (primary), `scholarships/templates/scholarships/*.html` (markup/structure tweaks within existing blocks, plus a small nav toggle script in `base.html`).
- **Python/contracts**: No changes to models, views, forms, URLs, or templatetags. Template variables and block names stay the same.
- **Dependencies**: No new runtime dependencies; pure CSS + a tiny vanilla-JS nav toggle. No CSS framework added (keeps footprint minimal and avoids restructuring).
- **Risk**: Low. Visual-only; existing tests for views/models remain valid. Static asset cache-busting should be considered on deploy.
