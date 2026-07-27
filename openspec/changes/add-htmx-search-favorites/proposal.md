## Why

The scholarship list currently requires a full page reload on every filter change, which feels slow and jarring on mobile, and the app offers no way for a student to save scholarships they care about for later. Adding async (HTMX) live filtering and a favorites feature closes the two largest gaps against the project's grading rubric — the "Rich interface / HTMX" and "User input (extensive)" tiers — while reinforcing the database-schema, business-logic, templates, and test categories.

## What Changes

- Introduce **HTMX-powered live search and filtering**: as the user types or changes a filter on `/scholarships/`, the results list updates asynchronously by swapping an HTML fragment, with no full page reload. Non-HTMX (progressive-enhancement) requests keep working and return the full page.
- Add a **Favorite** model linking a `User` to a `Scholarship` with a unique constraint, so an authenticated user can favorite and unfavorite scholarships.
- Add authenticated **favorite/unfavorite endpoints** (HTMX partial responses) plus a **"My Favorites" page** reachable from the profile and navigation.
- Render a favorite toggle control on each scholarship card/row and on the detail page; the toggle updates in place via HTMX.
- Load the **htmx** client library (via a static asset / CDN snippet in the base template) and add `HX-Request`-aware handling to the list and favorite views.
- Add **pagination** to the scholarship list so async searching stays fast as the dataset grows.
- Expand **tests** (models, views, forms, auth, HTMX partial responses, favorites) and update **README** docs (new URLs, HTMX dependency, deployment notes).

## Capabilities

### New Capabilities
- `scholarship-search`: Async, progressive-enhancement search and filtering of the scholarship list. The list view serves the full page to normal requests and returns a results HTML fragment to HTMX requests, updating the list in place as filters change.
- `scholarship-favorites`: Authenticated users can save scholarships to a personal favorites list. Owns a `Favorite` model (unique per user+scholarship) plus favorite/unfavorite actions and a "My Favorites" view.

### Modified Capabilities
<!-- None. The new behavior is additive; the existing scholarship-submission and scholarship-models requirements are unchanged. -->

## Impact

- **Code**: `scholarships/models.py` (new `Favorite` model + migration), `scholarships/views.py` (HTMX-aware list view, pagination, favorite/unfavorite views, favorites list view), `scholarships/forms.py` (unchanged filter form, reused), `scholarships/urls.py` (new routes), `scholarships/admin.py` (register `Favorite`).
- **Templates**: `base.html` (load htmx + shared JS), `scholarship_list.html` (extract a reusable `_scholarship_results.html` partial incl. favorite toggle), `scholarship_detail.html` (favorite toggle), new `_scholarship_card.html`, `_favorite_button.html`, `favorites.html`; update `profile.html` / nav with a Favorites link.
- **Dependencies**: No new Python package required; htmx (~14 KB JS) is loaded as a static asset (vendored) or via CDN snippet in `base.html`.
- **Data**: One new migration adding the `Favorite` table with foreign keys to `User` and `Scholarship` and a unique-together constraint.
- **Tests / Docs**: Expanded `scholarships/tests.py`; README API table and deployment notes updated.
- **Risk**: Low. Filtering logic is reused; HTMX is additive (graceful fallback to full-page rendering when JS is disabled).
