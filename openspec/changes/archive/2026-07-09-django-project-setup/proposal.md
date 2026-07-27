## Why

The project currently exists as an empty Python skeleton with no runnable application. To deliver the scholarship discovery and request features, we need a Django project with models for the three core entities and a fully functional development environment.

## What Changes

- Scaffold a Django project using `django-admin startproject`
- Create a Django app for scholarships using `manage.py startapp`
- Design Django models for User, Scholarship, and ScholarshipRequest with appropriate fields
- Implement `__str__()` methods on all models for admin usability
- Update `pyproject.toml` to include Django as a dependency
- Add Django to the development tooling configuration

## Capabilities

### New Capabilities
- `django-project`: Django project and app scaffold with settings and URLs configured
- `scholarship-models`: Django model definitions for User, Scholarship, and ScholarshipRequest with `__str__()` methods

### Modified Capabilities
- `project-scaffold`: Update development tooling to include Django; replace stub modules with actual Django model files

## Impact

- New dependency: Django (added to pyproject.toml)
- New files: Django project config, app files, model definitions, migrations
- Existing stub modules in `src/scholarship_finder/` replaced by Django app structure
- Development flow changes: requires `manage.py runserver`, `manage.py makemigrations`, etc.
