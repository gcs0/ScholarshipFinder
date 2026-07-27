# scholarship-search Specification

## ADDED Requirements

### Requirement: Scholarship list renders the full page for normal requests
The app SHALL serve a full HTML page at `/scholarships/` (URL name `scholarship-list`) that includes the filter form and the scholarship results, preserving the existing behavior for non-JavaScript clients.

#### Scenario: Normal GET returns the full page
- **WHEN** a client issues a normal GET to `/scholarships/` without an `HX-Request` header
- **THEN** the response SHALL be a full HTML page that includes the filter form and the results region
- **AND** the response status SHALL be `200`

#### Scenario: Filters still apply on full-page requests
- **WHEN** a client issues a normal GET to `/scholarships/?scholarship_name=xxx`
- **THEN** the returned full page SHALL display only scholarships matching the provided filters
- **AND** the previously submitted filter values SHALL be preserved in the rendered form

### Requirement: Scholarship list returns a results fragment for HTMX requests
The app SHALL detect HTMX requests (via the `HX-Request: true` header) on `/scholarships/` and respond with only the results HTML fragment instead of the full page, so the results region can be swapped in place.

#### Scenario: HTMX GET returns a fragment
- **WHEN** a client issues a GET to `/scholarships/` carrying the `HX-Request: true` header
- **THEN** the response SHALL contain only the results fragment markup (not the full `<html>` document or the filter form chrome)
- **AND** the response status SHALL be `200`

#### Scenario: HTMX GET applies the submitted filters
- **WHEN** a client issues an HTMX GET to `/scholarships/?scholarship_name=xxx&section=IV`
- **THEN** the returned fragment SHALL list only scholarships matching those filters

### Requirement: Filter form issues HTMX requests
The filter form on the scholarship list SHALL be configured to submit via HTMX so that changing any filter updates the results region asynchronously without a full page reload.

#### Scenario: Filter form targets the results region
- **WHEN** the scholarship list page is rendered
- **THEN** the filter form SHALL include HTMX attributes (`hx-get`, `hx-target`, `hx-trigger`) that POST/GET the form to `/scholarships/` and swap the results region

#### Scenario: Typing triggers a debounced search
- **WHEN** the `scholarship_name` text input is configured for live search
- **THEN** it SHALL use a debounced `hx-trigger` (e.g. `keyup changed delay:400ms`) so a request is not sent on every keystroke

#### Scenario: Non-HTMX fallback works
- **WHEN** JavaScript is disabled and the form is submitted normally
- **THEN** the form SHALL still perform a standard GET to `/scholarships/` and render the full filtered page

### Requirement: Search results are paginated
The scholarship list SHALL paginate results to keep rendering fast, and pagination SHALL work both in full-page and HTMX modes.

#### Scenario: Large result sets are paginated
- **WHEN** more scholarships exist than the configured page size
- **THEN** the results SHALL be split across pages with navigation controls

#### Scenario: Pagination preserves active filters
- **WHEN** a user follows a pagination link while filters are active
- **THEN** the active filter parameters SHALL be preserved across pages

#### Scenario: HTMX pagination swaps the results fragment
- **WHEN** a user follows a pagination link in HTMX mode
- **THEN** only the results fragment SHALL be returned and swapped
