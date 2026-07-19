# ScholarshipFinder

A Python-based project to support scholarship discovery and scholarship request submission.

## Project Outline

ScholarshipFinder is designed around three core entities:

- **User**: student account/profile information.
- **Scholarship**: scholarship listings and details.
- **Scholarship Request**: user-submitted requests for scholarships not yet listed.

Main user flow:

1. Browse scholarships.
2. Filter by education, discipline, and prefecture.
3. View details (requirements, award, deadlines).
4. Submit missing scholarship requests (authenticated users).

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
| `/scholarships/` | GET | `scholarship_list` | Query: `education_level`, `discipline`, `prefecture` (optional) | Rendered scholarship list (HTML) |
| `/scholarships/<int:pk>/` | GET | `scholarship_detail` | `pk`: int — scholarship ID | Rendered scholarship detail (HTML) |
| `/requests/new/` | GET, POST | `request_form` | POST: `user`, `scholarship_name`, `provider`, `award_amount`, `notes` | GET: form page (HTML); POST: success page (HTML) |
| `/users/new/` | GET, POST | `user_create` | POST: `name`, `email`, `education`, `discipline`, `prefecture` | GET: registration form (HTML); POST: redirect to user detail |
| `/users/<int:pk>/` | GET | `user_detail` | `pk`: int — user ID | Rendered user profile (HTML) |

## Suggested Structure

```text
ScholarshipFinder/
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
└── tests/
```
