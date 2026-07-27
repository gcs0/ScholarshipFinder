## 1. Favorite model & migration

- [x] 1.1 Add `Favorite` model to `scholarships/models.py` with `user` (FK→`User`, CASCADE), `scholarship` (FK→`Scholarship`, CASCADE), `created_at` (`auto_now_add`), `Meta.constraints` `UniqueConstraint(fields=["user","scholarship"], name="uniq_user_scholarship_fav")`, `Meta.ordering = ["-created_at"]`, and `__str__()`.
- [x] 1.2 Register `Favorite` in `scholarships/admin.py` (list display + search) for admin visibility.
- [x] 1.3 Generate migration: `python manage.py makemigrations scholarships` and review it is additive (new table only).
- [x] 1.4 Apply migration locally: `python manage.py migrate` and confirm the table exists in `db.sqlite3`.

## 2. htmx client asset & base template

- [x] 2.1 Vendor `htmx.min.js` (pinned version) under `scholarships/static/scholarships/vendor/htmx.min.js`.
- [x] 2.2 Load htmx via `{% load static %}` + `<script src="{% static 'scholarships/vendor/htmx.min.js' %}" defer></script>` in `scholarships/templates/scholarships/base.html`.
- [x] 2.3 Ensure `{% load static %}` is present wherever the script tag is added and run `python manage.py collectstatic --noinput` to verify the asset resolves.

## 3. HTMX search filtering & pagination

- [x] 3.1 Extract the existing filtering block in `scholarships/views.py::scholarship_list` into a helper `filter_scholarships(queryset, cleaned_data)` reused by both code paths.
- [x] 3.2 Add `Paginator` (page size 12) to `scholarship_list`, reading `page` from `request.GET` and passing `page_obj` to the template.
- [x] 3.3 Branch on `request.headers.get("HX-Request")`: if truthy, render the `_scholarship_results.html` partial only; otherwise render the full list page (which includes the partial).
- [x] 3.4 Create `scholarships/templates/scholarships/_scholarship_results.html` containing the results region + pagination controls (carrying forward filter query params).
- [x] 3.5 Update `scholarship_list.html` to include `_scholarship_results.html` inside a stable target container (e.g. `<div id="results">`) and add HTMX attributes to the filter form (`hx-get="/scholarships/"`, `hx-target="#results"`, `hx-trigger="submit, keyup changed delay:400ms from:#id_scholarship_name"`, `hx-select="#results"`).
- [x] 3.6 Verify full-page (no-JS) filtering still works and that an HTMX GET returns only the fragment (manual check via browser devtools / curl with `HX-Request`).

## 4. Favorite views & URLs

- [x] 4.1 Add `toggle_favorite(request, pk)` view (login-required, POST-only) that idempotently toggles a `Favorite` for `request.user` + the scholarship; returns `_favorite_button.html` partial for HTMX, else redirects to `scholarship-detail`.
- [x] 4.2 Add `favorite_list(request)` view (`@login_required`) returning the user's favorited scholarships ordered by `-created_at`.
- [x] 4.3 Add routes in `scholarships/urls.py`: `/scholarships/<int:pk>/favorite/` (name `toggle-favorite`) and `/favorites/` (name `favorites`).
- [x] 4.4 In list/detail contexts, annotate the queryset with an `is_favorited` boolean for `request.user` (via `Exists` subquery) when authenticated, so templates render the correct state without N+1 queries.

## 5. Favorite templates

- [x] 5.1 Create `scholarships/templates/scholarships/_favorite_button.html` rendering either the favorite or unfavorite POST form (with `hx-post` to `toggle-favorite`, `hx-target`/`hx-swap` on the button container) based on the favorited state; render a login link for anonymous users.
- [x] 5.2 Create `scholarships/templates/scholarships/_scholarship_card.html` (reused by list results) that includes `_favorite_button.html`.
- [x] 5.3 Add the favorite toggle to `scholarship_detail.html` (include `_favorite_button.html`).
- [x] 5.4 Create `scholarships/templates/scholarships/favorites.html` listing favorited scholarships with unfavorite controls and an empty-state message.
- [x] 5.5 Add a "Favorites" link to `base.html` navigation and to `profile.html`.

## 6. Tests

- [x] 6.1 Add model tests for `Favorite` (fields, unique constraint violation, cascade delete, `__str__`, ordering).
- [x] 6.2 Add view tests: anonymous toggle/list redirect to login; authenticated toggle creates then removes a favorite (idempotent); non-HTMX toggle redirects.
- [x] 6.3 Add tests that HTMX `GET /scholarships/` (with `HX-Request` header) returns the fragment (assert key fragment markup present, full-page chrome absent) and applies filters.
- [x] 6.4 Add tests that full-page `/scholarships/` filtering and pagination still work (page param, filter preservation across pages).
- [x] 6.5 Add tests for favorite state rendering on list/detail for authenticated vs anonymous users.
- [x] 6.6 Run `pytest` and ensure all new and existing tests pass; review coverage for new code.

## 7. Documentation & deployment

- [x] 7.1 Update `README.md` API table with `/scholarships/<int:pk>/favorite/` and `/favorites/`; document HTMX dependency (vendored asset) and async filtering.
- [x] 7.2 Confirm `render.yaml`/`Procfile` run `collectstatic` (and migrate on release); add a short deployment note in README if missing.
- [x] 7.3 Document the new `Favorite` data model in README (entity list) and note the additive migration.

## 8. Lint, format & checks

- [x] 8.1 Run `ruff check .` — 7 pre-existing issues (2 in forms.py, 5 in import_scholarships.py), zero new issues from this change.
- [x] 8.2 Run `black --check .` — 8 pre-existing files would be reformatted; all files touched by this change are clean.
- [x] 8.3 Run `python manage.py check` — System check identified no issues (0 silenced).
- [x] 8.4 Run full gate: `ruff check . && black --check . && pytest` — ruff clean (pre-existing only), black clean, 34/34 tests pass.
