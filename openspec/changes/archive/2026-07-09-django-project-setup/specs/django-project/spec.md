## ADDED Requirements

### Requirement: Django project scaffold
The project SHALL include a Django project scaffold created with `django-admin startproject`.

#### Scenario: manage.py exists
- **WHEN** the repository root is inspected
- **THEN** a `manage.py` file SHALL exist

#### Scenario: Django project package exists
- **WHEN** the repository root is inspected
- **THEN** a Django project package directory SHALL exist containing `settings.py`, `urls.py`, `wsgi.py`, and `asgi.py`

#### Scenario: Settings configure database
- **WHEN** `settings.py` is parsed
- **THEN** it SHALL contain a `DATABASES` configuration (defaulting to SQLite)

### Requirement: Scholarships Django app
The project SHALL include a Django app named `scholarships` created with `manage.py startapp`.

#### Scenario: App directory exists
- **WHEN** the repository root is inspected
- **THEN** a `scholarships/` app directory SHALL exist

#### Scenario: App is registered
- **WHEN** `settings.py` is parsed
- **THEN** the `INSTALLED_APPS` list SHALL include `scholarships`

### Requirement: Django dependency
Django SHALL be listed as a project dependency.

#### Scenario: Django in pyproject.toml
- **WHEN** `pyproject.toml` is parsed
- **THEN** it SHALL include `django` in the project dependencies or dependency groups
