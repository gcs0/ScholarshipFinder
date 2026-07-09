## Context

The project README describes three core entities (User, Scholarship, ScholarshipRequest) and a user flow for browsing, filtering, viewing, and submitting scholarship requests. There is currently no Django project, no database schema, and no runnable application. The archived "initial-project-setup" change established a basic project-scaffold spec that references stub modules under `src/scholarship_finder/`, but Django `startproject` creates its own directory structure that will replace or wrap that layout.

## Goals / Non-Goals

**Goals:**
- Scaffold a Django project at the repository root using `django-admin startproject`
- Create a Django app (e.g., `scholarships`) with models for all three core entities
- Implement `__str__()` methods on all models for admin usability
- Add Django to pyproject.toml dependencies
- Ensure `manage.py` is functional (creates db tables, can run)
- Update the project-scaffold spec to reflect Django-based structure

**Non-Goals:**
- No admin configuration or custom admin classes
- No views, templates, URLs, or REST API endpoints
- No authentication or user registration flows
- No migrations beyond the initial `makemigrations` + `migrate`
- No deployment configuration

## Decisions

- **Django project location**: Place `manage.py` and the Django project package (`config/`) at the repository root level (standard Django convention). This means the project root is the Django project root.
- **App name**: `scholarships` — matches the domain and stays concise
- **Model fields**: Use Django's built-in `AbstractUser` for user auth if needed; otherwise keep a simple model matching the README fields directly
- **Database**: SQLite (Django default) for development simplicity
- **Django version**: Latest stable (5.x) pinned in pyproject.toml

## Risks / Trade-offs

- **Django project at root vs src-layout**: The README suggests `src/` layout but Django's `startproject` places files at root by default. Trade-off: simpler Django workflow vs. pure src-layout. Decided to follow Django conventions.
- **Custom User model vs. standalone model**: A standalone User model is simpler for now but lacks Django auth integration. Decided to keep it simple — auth can be added later.
- **Existing stub files**: The archived spec expects stub modules under `src/scholarship_finder/`. These will be replaced by Django model files. The delta spec will update this requirement.
