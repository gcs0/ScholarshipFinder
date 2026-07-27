# ScholarshipFinder

A Python-based project to support scholarship discovery and scholarship request submission.

## Project Outline

ScholarshipFinder is designed around four core entities:

- **User**: student account/profile information.
- **Scholarship**: scholarship listings and details.
- **Scholarship Request**: user-submitted requests for scholarships not yet listed.
- **Favorite**: a user's saved scholarship (many-to-one to `User` and `Scholarship`).

Main user flow:

1. Browse scholarships.
2. Filter by education, discipline, and prefecture.
3. View details (requirements, award, deadlines).
4. Submit missing scholarship requests (authenticated users).
5. Save scholarships to a personal favorites list (authenticated users).

## Development Environment

This project uses a **uv-managed virtual environment**.

### 1) Create and activate environment

```bash
uv venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

### 2) Install development tools

```bash
uv pip install black ruff pytest pytest-cov
```

## Tooling

Configured in `pyproject.toml`:

- **Formatter**: `black`
- **Linter**: `ruff`
- **Tests**: `pytest`
- **Coverage**: `pytest-cov`

### Common commands

```bash
ruff check .
black .
pytest
```

## Repository Hygiene

Tracked config files:

- `.gitignore`
- `pyproject.toml`
- `README.md`

Ignored by `.gitignore`:

- `.venv/`
- Python cache files
- test/coverage caches
- editor/OS artifacts

## API Reference

| URL | Method | View | Arguments | Returns |
|-----|--------|------|-----------|---------|
| `/` | GET | `home` | — | Rendered home page (HTML) |
| `/scholarships/` | GET | `scholarship_list` | Query: `education_level`, `discipline`, `prefecture` (optional) | Rendered scholarship list (HTML). HTMX requests (`HX-Request` header) receive only the results fragment; normal requests receive the full page. Results are paginated (12/page). |
| `/scholarships/<int:pk>/` | GET | `scholarship_detail` | `pk`: int — scholarship ID | Rendered scholarship detail (HTML) |
| `/scholarships/<int:pk>/favorite/` | POST | `toggle_favorite` | `pk`: int — scholarship ID | Toggles the logged-in user's favorite on a scholarship. HTMX requests receive the `_favorite_button.html` partial; non-HTMX requests redirect to the scholarship detail. Requires login. |
| `/favorites/` | GET | `favorite_list` | — | Lists the logged-in user's saved scholarships (HTML). Requires login. |
| `/requests/new/` | GET, POST | `request_form` | POST: `user`, `scholarship_name`, `provider`, `award_amount`, `notes` | GET: form page (HTML); POST: success page (HTML) |
| `/users/new/` | GET, POST | `user_create` | POST: `name`, `email`, `education`, `discipline`, `prefecture` | GET: registration form (HTML); POST: redirect to user detail |
| `/users/<int:pk>/` | GET | `user_detail` | `pk`: int — user ID | Rendered user profile (HTML) |

## Async UI (HTMX)

The scholarship list uses [htmx](https://htmx.org) (vendored at
`scholarships/static/scholarships/vendor/htmx.min.js`) so the filter form and
pagination update the results region **without a full page reload**. This is a
progressive enhancement: with JavaScript disabled, the same `/scholarships/`
URL returns the full filtered page. Favorite/unfavorite toggles likewise swap a
small partial via HTMX.

## Data Model

- `User` — student profile (custom `AbstractUser`; `AUTH_USER_MODEL`).
- `Scholarship` — scholarship listing.
- `ScholarshipRequest` — user-submitted request + admin review workflow.
- `Favorite` — a saved scholarship (`user` + `scholarship` with a unique
  constraint; cascade-deletes with either side). Added by migration
  `0006_favorite` (additive).

## Suggested Structure

```text
ScholarshipFinder/
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
└── tests/
```

## Deployment

The app is configured for [Render](https://render.com) via `render.yaml` and
served by **gunicorn** (`Procfile`). Static files are served by
**WhiteNoise**.

Render build/release steps (already wired in `render.yaml`):

1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --noinput` — gather static assets.
3. `python manage.py migrate` — apply migrations (the `Favorite` table is
   additive; safe on existing data).
4. `python setup_admin.py` — create the admin user.
5. Start: `gunicorn config.wsgi --log-file -`.

### Run locally

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Environment variables (see `render.yaml` / `.env.example`):
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
`SECURE_SSL_REDIRECT`, `DATABASE_URL`, `ADMIN_PASSWORD`.
