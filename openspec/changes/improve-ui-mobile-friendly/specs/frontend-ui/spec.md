## ADDED Requirements

### Requirement: Design token system
The presentation layer SHALL define a centralized set of CSS custom properties covering brand/color, typography scale, spacing, border radius, and elevation (shadow), and existing legacy variables (e.g. `--color-text`, `--color-border`, `--spacing-unit`, `--max-width`) SHALL be expressed as references to these tokens.

#### Scenario: Tokens are defined once at the root
- **WHEN** the stylesheet's `:root` (or equivalent top-level) rule is inspected
- **THEN** it SHALL declare color, type-scale, spacing, radius, and shadow tokens used by the rest of the stylesheet

#### Scenario: Legacy variables remain valid
- **WHEN** an existing rule references a legacy variable such as `--color-text` or `--color-border`
- **THEN** the variable SHALL resolve correctly because legacy names are aliased to the new tokens

### Requirement: Mobile-first responsive layout
Every page SHALL be usable from a 320px viewport upward using a mobile-first stylesheet that progressively enhances via `min-width` media queries at documented breakpoints (480px, 768px, 1024px).

#### Scenario: Page is usable on a narrow phone
- **WHEN** any page is rendered at a viewport width of 360px
- **THEN** no horizontal scrolling SHALL be required to read primary content, and text SHALL remain legible without zooming

#### Scenario: Layout adapts to larger screens
- **WHEN** the viewport is widened to 768px or greater
- **THEN** the layout SHALL progressively enhance to a multi-column presentation where applicable (e.g. scholarship table, filter grid, detail list)

### Requirement: Collapsible site navigation
The site header SHALL render all primary navigation links and, on viewports below the navigation breakpoint, SHALL collapse them behind a single toggle button that exposes the links on demand while preserving keyboard and screen-reader accessibility.

#### Scenario: Navigation collapses on small screens
- **WHEN** the header is rendered at a viewport width below the navigation breakpoint
- **THEN** the navigation links SHALL be hidden by default and a visible toggle button SHALL be present

#### Scenario: Toggle reveals navigation accessibly
- **WHEN** a user activates the navigation toggle
- **THEN** the navigation links SHALL become visible, the toggle's `aria-expanded` state SHALL reflect whether the menu is open, and the links SHALL remain reachable via keyboard

#### Scenario: Navigation works without JavaScript
- **WHEN** JavaScript is disabled in the browser
- **THEN** the primary navigation links SHALL still be reachable (e.g. rendered as a visible fallback list)

### Requirement: Responsive scholarship list
The scholarship list SHALL present a dense comparison table on wider screens and SHALL transform into a stacked, card-style layout on narrow screens without duplicating the row markup.

#### Scenario: Table on desktop
- **WHEN** the scholarship list is rendered at a viewport width of 768px or greater
- **THEN** it SHALL display scholarships as a table with one row per scholarship and column headers

#### Scenario: Stacked cards on mobile
- **WHEN** the scholarship list is rendered at a viewport width below 768px
- **THEN** each scholarship SHALL be displayed as a stacked block whose cells are labeled with their column name, and the page SHALL NOT require horizontal scrolling to read any scholarship

### Requirement: Consistent interactive components
Buttons, badges, cards, alerts, and form inputs SHALL share a consistent visual treatment (sizing, padding, radius, color, focus style) derived from the design tokens, and interactive elements SHALL meet a minimum 44×44px hit area on touch viewports.

#### Scenario: Buttons share a base style
- **WHEN** any `<button>` or `.button` element is rendered
- **THEN** it SHALL apply the shared button styling (padding, radius, font, focus-visible outline) from the component layer

#### Scenario: Touch targets are large enough on mobile
- **WHEN** an interactive element is rendered at a viewport width below 480px
- **THEN** its tappable area SHALL be at least 44×44 CSS pixels

### Requirement: Mobile-friendly form inputs
Form text inputs, selects, and textareas SHALL render at `width: 100%` of their container with a font size of 1rem (16px) and comfortable vertical padding so they do not trigger auto-zoom on mobile platforms and remain easy to tap.

#### Scenario: Inputs do not trigger mobile zoom
- **WHEN** a text input, select, or textarea is focused on a mobile viewport
- **THEN** its font-size SHALL be at least 16px and the OS SHALL not perform a layout zoom

### Requirement: Accessibility baseline
The presentation layer SHALL meet WCAG AA color contrast (at least 4.5:1 for body text and 3:1 for large text and UI component boundaries), SHALL keep visible keyboard focus indicators, and SHALL honor the user's reduced-motion preference.

#### Scenario: Body text meets contrast
- **WHEN** the foreground/background color pair for body text is evaluated
- **THEN** the contrast ratio SHALL be at least 4.5:1

#### Scenario: Focus remains visible
- **WHEN** an interactive element receives keyboard focus
- **THEN** a visible focus indicator SHALL be displayed against the element's current background

#### Scenario: Reduced motion is respected
- **WHEN** the user agent reports `prefers-reduced-motion: reduce`
- **THEN** non-essential animations and transitions (including the clamp height transition) SHALL be disabled

### Requirement: Preservation of application structure
This change SHALL be confined to static assets and templates. It SHALL NOT alter Django models, views, URL configurations, forms, or template tag signatures, and it SHALL preserve existing template block names (`title`, `content`, `extra_js`) and the context variables passed to each template.

#### Scenario: No backend changes
- **WHEN** the change is applied
- **THEN** `models.py`, `views.py`, `urls.py`, and `forms.py` SHALL be unchanged in their public behavior and signatures

#### Scenario: Template contract is preserved
- **WHEN** the templates are rendered with their existing view contexts
- **THEN** all blocks and context variables used prior to the change SHALL continue to resolve without errors
