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

## Suggested Structure

```text
ScholarshipFinder/
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
└── tests/
```
