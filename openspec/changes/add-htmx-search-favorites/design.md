## Context

ScholarshipFinder is a Django 5 app (`config` project, single `scholarships` app) using server-rendered templates with a `base.html` layout. The current `/scholarships/` view (`scholarship_list`) filters via a `ScholarshipFilterForm` and re-renders the entire page on every submit. Models already exist for `User` (custom `AbstractUser`), `Scholarship`, and `ScholarshipRequest` with foreign-key relationships. There is no favorites concept and no async UI today. This change adds two capabilities — `scholarship-search` (HTMX live filtering + pagination) and `scholarship-favorites` (a `Favorite` model + toggle + "My Favorites" page) — both delivered as progressive enhancements over the existing server-rendered flow.

## Goals / Non-Goals

**Goals:**
- Make `/scholarships/` filtering update asynchronously via HTMX while keeping full-page rendering as the fallback.
- Reuse the existing `ScholarshipFilterForm` and filtering logic so behavior is unchanged for normal requests.
- Introduce a `Favorite` model with clean foreign keys + uniqueness and expose favorite/unfavorite + a favorites list.
- Keep favorite toggles working both with and without HTMX.
- Add tests for all new behavior and update README/deployment docs.

**Non-Goals:**
- No REST/JSON API (HTML fragments only).
- No re-architecture of auth (reuse Django auth + existing `RegistrationForm`/`CustomLoginForm`).
- No redesign of admin request review (favorites are a separate, user-facing feature).
- No recommendation/matching engine; favorites are a simple saved list.
- No per-user personalization of search ranking.

## Decisions

### Decision 1: Detect HTMX via `HX-Request` header and branch the template/response
**Choice:** In `scholarship_list`, read `request.headers.get("HX-Request")`. When truthy, render only the `_scholarship_results.html` partial; otherwise render the full page (which itself includes the partial).
**Rationale:** Single source of truth for the results markup (the partial) is included by the full-page template, so the two paths can never drift. No separate view or URL is needed for the async path.
**Alternatives considered:**
- *Separate `/scholarships/search/` endpoint for HTMX*: rejected — duplicates URL/filter logic and breaks bookmarkable filter URLs.
- *Returning JSON and rendering client-side*: rejected — would require a JS templating layer and lose Django template/CSRF reuse; conflicts with the "complete separation of concerns via templates" goal.

### Decision 2: Vendor htmx as a static asset (with CDN fallback) loaded in `base.html`
**Choice:** Add `scholarships/static/scholarships/vendor/htmx.min.js` and load it via `{% static %}` in `base.html`. Optionally include a SRI-pinned CDN `<script>` as fallback.
**Rationale:** No new Python dependency; works offline and on Render without external network calls; keeps deployment self-contained (supports the deployment-rubric goal). Vendoring one small file is low-maintenance.
**Alternatives considered:**
- *`django-htmx` pip package*: rejected as a hard dependency to avoid new install steps; we only need the client library. (Could be added later purely for the middleware/debug helper.)
- *CDN-only*: rejected — adds an external runtime dependency and fails behind strict networks.

### Decision 3: Favorite toggle as a single POST form per control, returning a partial
**Choice:** `_favorite_button.html` renders either the "favorite" or "unfavorite" form depending on current state. Each form POSTs to a single endpoint (e.g. `/scholarships/<pk>/favorite/`) and returns `_favorite_button.html` rendered with the toggled state for HTMX requests, or a redirect for non-HTMX requests.
**Rationale:** POST (not GET) for state mutation; one endpoint that toggles idempotently keeps URLs simple and matches the spec's idempotency scenarios. Returning the same partial the control already renders makes the HTMX swap a drop-in.
**Alternatives considered:**
- *Two separate `/favorite/` and `/unfavorite/` endpoints*: acceptable but doubles routes; the toggle semantics are clearer with a single idempotent endpoint. (We'll still name it clearly to convey mutation.)
- *`DELETE` for unfavorite*: rejected — requires JS to send the method; plain POST forms work without JS.

### Decision 4: `Favorite` model with `UniqueConstraint` on (`user`, `scholarship`)
**Choice:** `Favorite(user FK CASCADE, scholarship FK CASCADE, created_at auto_now_add)` with `Meta.constraints = [UniqueConstraint(fields=["user","scholarship"], name="uniq_user_scholarship_fav")]` and `ordering = ["-created_at"]`.
**Rationale:** DB-level guarantee of uniqueness (stronger than app-level checks); cascading deletes keep data tidy when a user or scholarship is removed. Constraint is preferred over the legacy `unique_together` per Django best practice.
**Alternatives considered:**
- *`unique_together`*: works but is the older style; constraint is more explicit and future-proof.

### Decision 5: Reuse existing filter logic; add pagination via Django's `Paginator`
**Choice:** Extract the existing filtering block in `scholarship_list` into a small helper (e.g. `filter_scholarships(queryset, cleaned_data)`) reused by both full-page and HTMX paths. Wrap the filtered queryset in `Paginator(page_size=N)` (e.g. 12).
**Rationale:** Avoids behavior drift, keeps the diff focused, and gives pagination for free in both modes. Pagination links will carry forward query params (filters) via `request.GET.copy()`.
**Alternatives considered:**
- *Infinite scroll with HTMX `hx-get` on the last row*: nice UX but adds complexity; deferred to a follow-up. Standard pagination is sufficient for the rubric.

### Decision 6: Annotate "favorited" state efficiently for list rendering
**Choice:** When the user is authenticated, annotate the scholarship queryset with a boolean (e.g. via `Exists` subquery on `Favorite` filtered by `user=request.user`) so the template can render the correct toggle state without N+1 queries.
**Rationale:** Keeps the list page efficient as the dataset grows and avoids a per-row DB hit.
**Alternatives considered:**
- *Prefetch related + Python set lookup*: also viable but the `Exists` annotation is idiomatic and a single query.

## Risks / Trade-offs

- **Filter form GET vs. POST**: HTMX forms work best with GET for bookmarkable filters; we'll keep GET (matches current behavior). *Mitigation:* ensure CSRF is not required for GET (it isn't) and that ` ScholarshipFilterForm` validates `request.GET`.
- **Award-amount filtering is in-Python** (iterates scholarships): *Mitigation* — apply it before pagination so page size stays bounded; acceptable for current dataset size, and noted as a future DB-optimization opportunity.
- **Anonymous users see favorite buttons**: *Mitigation* — gate the toggle behind `{% if user.is_authenticated %}` and link to login otherwise (spec scenario).
- **HTMX partials bypass some layout context**: *Mitigation* — partial templates intentionally contain only the results fragment; full context (e.g. filter form) is provided by the full-page path.
- **Migration on production DB**: *Mitigation* — the new `Favorite` table is additive; migration is reversible (`migrate scholarships 00xx` rollback drops only the new table). No data backfill required.

## Migration Plan

1. Add `Favorite` model and create migration `python manage.py makemigrations scholarships`; review the generated migration (additive only).
2. Apply with `python manage.py migrate` locally; verify in `db.sqlite3`.
3. Vendor `htmx.min.js` under static and load in `base.html`; run `python manage.py collectstatic --noinput` (Render build step already does this).
4. Deploy to Render (existing `render.yaml`/`Procfile` unchanged structurally); `migrate` runs via release command if configured, else run once after deploy.
5. **Rollback**: `python manage.py migrate scholarships <previous>` removes the `Favorite` table; revert code and templates. No user data outside the new table is affected.

## Open Questions

- Page size default (proposing **12**, divisible for responsive grids 2/3/4 columns) — confirm during implementation.
- Whether to additionally install `django-htmx` for the debug middleware — deferred (not required).
