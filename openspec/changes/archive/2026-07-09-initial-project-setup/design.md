## Context

The ScholarshipFinder repository currently contains only a README.md (project overview, tooling, suggested structure) and an AGENTS.md (opencode command aliases). There is no `pyproject.toml`, no `.gitignore`, no Python package structure, and no test scaffolding — development cannot begin until these are established.

## Goals / Non-Goals

**Goals:**
- Create a `pyproject.toml` with project metadata, dependency stubs, and tool configuration (black, ruff, pytest)
- Create a `.gitignore` appropriate for a Python project using uv
- Create the `src/scholarship_finder/` package with stub modules for the three core entities (User, Scholarship, ScholarshipRequest)
- Create a `tests/` directory with a placeholder test runner
- Ensure `ruff check .`, `black --check .`, and `pytest` pass from the root

**Non-Goals:**
- No business logic or entity implementations — only stub packages/modules
- No CI/CD pipeline
- No database setup or ORM configuration
- No user-facing interfaces (CLI, web, API)

## Decisions

- **Package name**: `scholarship_finder` (underscore convention matching PEP 8 for package names)
- **src-layout**: Using `src/` layout to enforce import discipline (prevents importing the package without installation)
- **Tooling versions**: Pin to latest stable versions of black, ruff, pytest compatible with Python 3.12+
- **uv**: Use `uv` for venv and dependency management as specified in README — `pyproject.toml` will include `[project.urls]`, `[dependency-groups]` for dev tooling

## Risks / Trade-offs

- **No dependency pinning initially**: The initial `pyproject.toml` won't pin exact versions. Mitigation: developers run `uv pip install` directly per the README instructions; explicit pinning can be added later in a separate change.
- **Stub modules may drift**: Without implemented logic, stub files may fall out of sync with actual entity designs. Mitigation: stubs should mirror the entity names from the README exactly.
